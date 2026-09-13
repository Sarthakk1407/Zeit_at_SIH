#!/usr/bin/env python3
"""realtime.py -- the live demo: headset mics in, cleaned voice out, on the Jetson.

    python3 realtime.py --onnx gtcrn_stream.onnx --list-devices
    python3 realtime.py --onnx gtcrn_stream.onnx --device "UMC404HD" --trt-fp16
    python3 realtime.py --onnx gtcrn_stream.onnx --device "UMC404HD" --cpu      # any laptop

    Press ENTER to toggle the model ON / OFF (the PS's live demonstration).
    Ctrl+C to stop; frame-time statistics are printed on exit.

Audio path: interface at 48 kHz (ch A = Mic 1 boom, ch B = Mic 2 reference)
-> stateful 3:1 decimation -> 16 kHz streaming model -> 1:3 interpolation ->
headphone / radio output. Runs on ONNX Runtime; with --trt-* it uses the
TensorRT execution provider, which builds and caches a TensorRT engine from
the ONNX file on first start (the first launch takes a minute).

This is the Lane B model only. Aux-IVA, the kurtosis classifier, BMRI and the
voice guard are the C++ engine's blocks and are not in this script.
"""
import argparse
import os
import queue
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import numpy as np                                             # noqa: E402
from scipy.signal import firwin, lfilter, lfilter_zi           # noqa: E402

from zeit.streaming import HOP, OnnxStreamer                   # noqa: E402

FS_IO, FS_MODEL, R = 48000, 16000, 3
BLOCK = HOP * R                                                # 768 samples = 16 ms


class Resampler:
    """Stateful 3:1 / 1:3 FIR resampling, continuous across blocks (~1 ms group delay each way)."""

    def __init__(self, chans):
        self.h = firwin(96, 7200, fs=FS_IO).astype(np.float64)
        self.zd = [lfilter_zi(self.h, 1.0) * 0 for _ in range(chans)]
        self.zu = lfilter_zi(self.h, 1.0) * 0

    def down(self, x):                                         # (chans, 768) -> (chans, 256)
        out = np.empty((x.shape[0], HOP), np.float32)
        for c in range(x.shape[0]):
            y, self.zd[c] = lfilter(self.h, 1.0, x[c], zi=self.zd[c])
            out[c] = y[::R]
        return out

    def up(self, x):                                           # (256,) -> (768,)
        z = np.zeros(BLOCK); z[::R] = x * R
        y, self.zu = lfilter(self.h, 1.0, z, zi=self.zu)
        return y.astype(np.float32)


def providers(a):
    cache = os.path.join(HERE, "trt_cache")
    if a.cpu:
        return ["CPUExecutionProvider"]
    trt = ("TensorrtExecutionProvider", dict(
        trt_engine_cache_enable=True, trt_engine_cache_path=cache,
        trt_fp16_enable=a.trt_fp16 or a.trt_int8, trt_int8_enable=a.trt_int8))
    if a.trt_fp16 or a.trt_int8 or a.trt_fp32:
        return [trt, "CUDAExecutionProvider", "CPUExecutionProvider"]
    return ["CUDAExecutionProvider", "CPUExecutionProvider"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True)
    ap.add_argument("--device", help="sounddevice name or index (both in and out)")
    ap.add_argument("--in-ch", type=int, nargs=2, default=[1, 2], help="Mic 1 and Mic 2 input channels (1-based)")
    ap.add_argument("--list-devices", action="store_true")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--trt-fp16", action="store_true")
    g.add_argument("--trt-int8", action="store_true")
    g.add_argument("--trt-fp32", action="store_true")
    g.add_argument("--cpu", action="store_true")
    ap.add_argument("--gain-db", type=float, default=0.0, help="output gain")
    a = ap.parse_args()

    import sounddevice as sd
    if a.list_devices:
        print(sd.query_devices()); return 0

    import onnx
    mics = onnx.load(a.onnx).graph.input[0].type.tensor_type.shape.dim[1].dim_value
    st = OnnxStreamer(a.onnx, mics, providers(a))
    print(f"  providers: {st.sess.get_providers()}")
    rs = Resampler(mics)
    gain = 10 ** (a.gain_db / 20)
    chans = [c - 1 for c in a.in_ch][:mics]
    state = dict(on=True)
    times = []

    # warm-up: first TensorRT call builds the engine; do it before audio starts
    for _ in range(20):
        st.process(np.zeros((mics, HOP), np.float32))
    st.reset()

    def toggle():
        while True:
            sys.stdin.readline()
            state["on"] = not state["on"]
            print(f"  model {'ON ' if state['on'] else 'OFF'}", flush=True)
    threading.Thread(target=toggle, daemon=True).start()

    def callback(indata, outdata, frames, t, status):
        if status:
            print(f"  audio status: {status}", flush=True)
        t0 = time.perf_counter()
        x = rs.down(indata[:, chans].T.astype(np.float64))
        y = st.process(x) if state["on"] else st.bypass(x)
        out = rs.up(y) * gain
        outdata[:] = np.repeat(out[:, None], outdata.shape[1], axis=1)
        times.append((time.perf_counter() - t0) * 1000)

    n_in = max(chans) + 1
    print(f"  {FS_IO} Hz, block {BLOCK} ({BLOCK / FS_IO * 1000:.0f} ms), mics on inputs {a.in_ch}. ENTER toggles, Ctrl+C stops.")
    try:
        with sd.Stream(device=a.device, samplerate=FS_IO, blocksize=BLOCK,
                       channels=(n_in, 2), dtype="float32", latency="low", callback=callback):
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    if times:
        t = np.array(times[50:] or times)
        print(f"\n  frames {len(t)}   mean {t.mean():.2f} ms   p99 {np.percentile(t, 99):.2f} ms   "
              f"max {t.max():.2f} ms   (budget {BLOCK / FS_IO * 1000:.0f} ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
