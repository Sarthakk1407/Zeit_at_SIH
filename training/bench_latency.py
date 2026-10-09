#!/usr/bin/env python3
"""bench_latency.py -- measure the streaming model the way the Jetson runs it.

    python bench_latency.py            # 3 inputs, 2000 frames, CPU

Builds the three-input GTCRN, exports the streaming ONNX file, verifies it
against PyTorch, then times ONNX Runtime one 16 ms frame at a time, carrying
the recurrent state between frames exactly as `jetson/realtime.py` does.
Every figure printed is measured on this machine; nothing is assumed. The
weights are untrained, which does not change the compute per frame.
"""
import argparse
import os
import platform
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import torch                                                   # noqa: E402

from export_onnx import NAMES_OUT, export, verify              # noqa: E402
from zeit.model import GTCRN, count_params                     # noqa: E402

HOP_MS = 16.0


def cpu_name():
    """The processor's marketing name, so the result says what it ran on."""
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        return winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
    except Exception:
        return platform.processor() or platform.machine()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mics", type=int, default=3)
    ap.add_argument("--frames", type=int, default=2000)
    ap.add_argument("--warmup", type=int, default=100)
    a = ap.parse_args()

    import onnxruntime as ort
    print("ANVIL voice lane -- streaming latency benchmark")
    print(f"cpu       {cpu_name()}")
    print(f"runtime   onnxruntime {ort.__version__}, CPU provider, 1 thread")
    torch.manual_seed(0)
    model = GTCRN(mics=a.mics).eval()
    print(f"model     GTCRN, {a.mics} inputs, {count_params(model):,} parameters")

    path = os.path.join(tempfile.mkdtemp(), "gtcrn_stream.onnx")
    export(model, path)
    print(f"export    streaming ONNX, {os.path.getsize(path) / 1024:.0f} KB")
    print("verify")
    ok = verify(model, path)
    if not ok:
        print("VERIFY FAILED"); return 1

    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 1
    sess = ort.InferenceSession(path, opts, providers=["CPUExecutionProvider"])
    conv, tra, inter = [s.numpy() for s in model.init_state(1)]
    rng = np.random.default_rng(0)
    frames = (rng.standard_normal((a.warmup + a.frames, 1, a.mics, 257, 1, 2)) * 0.1).astype(np.float32)
    times = []
    for i, f in enumerate(frames):
        t0 = time.perf_counter()
        _, conv, tra, inter = sess.run(NAMES_OUT, dict(frame=f, conv_cache=conv,
                                                      tra_cache=tra, inter_cache=inter))
        dt = (time.perf_counter() - t0) * 1000.0
        if i >= a.warmup:
            times.append(dt)
    t = np.array(times)
    p50, p95, p99 = np.percentile(t, [50, 95, 99])
    over = int((t > HOP_MS).sum())
    print(f"timing    {a.frames} frames of 16 ms, state carried frame to frame")
    print(f"  mean   {t.mean():6.3f} ms    p50  {p50:6.3f} ms    p95  {p95:6.3f} ms")
    print(f"  p99    {p99:6.3f} ms    max  {t.max():6.3f} ms")
    print(f"  real-time factor        {t.mean() / HOP_MS:.3f}   (1.0 = just real time)")
    print(f"  frames over budget      {over} / {a.frames}")
    print(f"  headroom at p99         {HOP_MS - p99:6.3f} ms of every 16 ms")
    print("RESULT    PASS -- faster than real time on one laptop CPU core"
          if p99 < HOP_MS and over == 0 else "RESULT    FAIL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
