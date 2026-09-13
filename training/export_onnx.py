#!/usr/bin/env python3
"""export_onnx.py -- trained checkpoint -> streaming ONNX file for the Jetson.

    python export_onnx.py runs/gtcrn_dualmic-1a2b3c4d/best.pt
    python export_onnx.py runs/.../best.pt --out gtcrn_stream.onnx

The exported model processes ONE 16 ms frame and carries its memory:

    inputs   frame        (1, mics, 257, 1, 2)   noisy STFT frame, real/imag
             conv_cache   (1, 6, 16, 10, 33)     past frames for the causal convs
             tra_cache    (6, 1, 16)             attention GRU states
             inter_cache  (4, 33, 8)             time-direction GRU states
    outputs  enhanced     (1, 257, 1, 2)         Mic 1's clean STFT frame
             conv_cache_out, tra_cache_out, inter_cache_out   feed back next frame

Three checks run before the file is trusted, and export fails if any fails:
  1. streaming PyTorch == whole-clip PyTorch     (the model really is causal)
  2. ONNX Runtime       == streaming PyTorch     (the export is faithful)
  3. every frame is finite
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import torch                                                   # noqa: E402

from zeit.config import Cfg                                    # noqa: E402
from zeit.model import GTCRN                                   # noqa: E402

TOL = 1e-4
NAMES_IN = ["frame", "conv_cache", "tra_cache", "inter_cache"]
NAMES_OUT = ["enhanced", "conv_cache_out", "tra_cache_out", "inter_cache_out"]


class StreamWrapper(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.m = model

    def forward(self, frame, conv_cache, tra_cache, inter_cache):
        return self.m.stream(frame, conv_cache, tra_cache, inter_cache)


def stream_torch(model, spec):
    """Run a (1,M,F,T,2) spectrum frame by frame; returns (1,F,T,2)."""
    conv, tra, inter = model.init_state(1)
    outs = []
    for t in range(spec.shape[3]):
        o, conv, tra, inter = model.stream(spec[:, :, :, t:t + 1], conv, tra, inter)
        outs.append(o)
    return torch.cat(outs, dim=2)


def stream_onnx(path, spec, model):
    import onnxruntime as ort
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    conv, tra, inter = [s.numpy() for s in model.init_state(1)]
    outs = []
    x = spec.numpy()
    for t in range(x.shape[3]):
        o, conv, tra, inter = sess.run(NAMES_OUT, dict(frame=x[:, :, :, t:t + 1], conv_cache=conv,
                                                      tra_cache=tra, inter_cache=inter))
        outs.append(o)
    return np.concatenate(outs, axis=2)


def export(model, path, opset=17):
    wrap = StreamWrapper(model).eval()
    frame = torch.randn(1, model.mics, 257, 1, 2)
    args = (frame, *model.init_state(1))
    kw = dict(input_names=NAMES_IN, output_names=NAMES_OUT, opset_version=opset)
    try:                                  # classic TorchScript exporter handles GRU cleanly
        torch.onnx.export(wrap, args, path, dynamo=False, **kw)
    except TypeError:                     # older torch without the dynamo switch
        torch.onnx.export(wrap, args, path, **kw)


def verify(model, path, frames=120):
    torch.manual_seed(0)
    spec = torch.randn(1, model.mics, 257, frames, 2) * 0.1
    with torch.no_grad():
        full = model(spec)
        strm = stream_torch(model, spec)
    d1 = float((full - strm).abs().max())
    onx = stream_onnx(path, spec, model)
    d2 = float(np.abs(onx - strm.numpy()).max())
    finite = bool(np.isfinite(onx).all())
    print(f"  streaming vs whole-clip (PyTorch)   max |diff| = {d1:.2e}   {'OK' if d1 < TOL else 'FAIL'}")
    print(f"  ONNX Runtime vs PyTorch streaming   max |diff| = {d2:.2e}   {'OK' if d2 < TOL else 'FAIL'}")
    print(f"  all outputs finite                  {'OK' if finite else 'FAIL'}")
    return d1 < TOL and d2 < TOL and finite


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("--out")
    ap.add_argument("--opset", type=int, default=17)
    a = ap.parse_args()

    ck = torch.load(a.checkpoint, map_location="cpu")
    cfg = Cfg(ck["cfg"])
    model = GTCRN(mics=cfg.model.mics)
    model.load_state_dict(ck["model"]); model.eval()
    out = a.out or os.path.join(os.path.dirname(a.checkpoint), "gtcrn_stream.onnx")

    export(model, out, a.opset)
    print(f"\n  exported  {out}  ({os.path.getsize(out) / 1024:.0f} KB)\n")
    if not verify(model, out):
        print("\n  !! verification FAILED -- do not deploy this file\n")
        return 1
    print("\n  verified. Next, on the Jetson:  bash jetson/build_engine.sh", out, "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
