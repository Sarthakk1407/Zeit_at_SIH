#!/usr/bin/env python3
"""enhance.py -- clean up recorded files with a checkpoint or the exported ONNX.

    python enhance.py runs/.../best.pt noisy_2ch.wav -o clean.wav
    python enhance.py runs/.../gtcrn_stream.onnx noisy_2ch.wav -o clean.wav
    python enhance.py runs/.../gtcrn_stream.onnx mic1.wav --ref mic2.wav -o clean.wav

Input is a 2-channel WAV (ch 1 = Mic 1 boom, ch 2 = Mic 2 reference), or two
mono files. Any sample rate; resampled to 16 kHz. With an .onnx file the audio
runs frame by frame through the same streamer the Jetson uses.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import soundfile as sf                                         # noqa: E402

from zeit.audio import resample                                # noqa: E402

SR = 16000


def load_mics(path, ref, mics):
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    chans = [resample(x[:, c], sr, SR) for c in range(x.shape[1])]
    if ref:
        r, sr2 = sf.read(ref, dtype="float32", always_2d=True)
        chans.append(resample(r[:, 0], sr2, SR))
    if len(chans) < mics:
        sys.exit(f"model needs {mics} microphone channel(s), input has {len(chans)}")
    L = min(len(c) for c in chans[:mics])
    return np.stack([c[:L] for c in chans[:mics]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", help="checkpoint .pt or exported .onnx")
    ap.add_argument("input")
    ap.add_argument("--ref", help="Mic 2 as a separate mono file")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    if a.model.endswith(".onnx"):
        from zeit.streaming import HOP, OnnxStreamer
        import onnx
        mics = onnx.load(a.model).graph.input[0].type.tensor_type.shape.dim[1].dim_value
        x = load_mics(a.input, a.ref, mics)
        st = OnnxStreamer(a.model, mics)
        n = x.shape[1] // HOP * HOP
        y = np.concatenate([st.process(x[:, i:i + HOP]) for i in range(0, n, HOP)])
    else:
        import torch
        from zeit.audio import istft, stft
        from zeit.config import Cfg
        from zeit.model import GTCRN
        ck = torch.load(a.model, map_location="cpu")
        mics = Cfg(ck["cfg"]).model.mics
        model = GTCRN(mics=mics); model.load_state_dict(ck["model"]); model.eval()
        x = load_mics(a.input, a.ref, mics)
        with torch.no_grad():
            y = istft(model(stft(torch.from_numpy(x)[None])), x.shape[1])[0].numpy()
    sf.write(a.out, y, SR, subtype="PCM_24")
    print(f"  {a.input} -> {a.out}  ({len(y) / SR:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
