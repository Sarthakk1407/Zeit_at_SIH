#!/usr/bin/env python3
"""quantize_onnx.py -- FP32 streaming ONNX -> INT8 (QDQ) ONNX, calibrated on real audio.

    python quantize_onnx.py runs/.../gtcrn_stream.onnx --calib-dir calib_wavs/
    python quantize_onnx.py runs/.../gtcrn_stream.onnx --calib-dir calib_wavs/ --frames 3000

Calibration feeds real noisy recordings (2-channel WAVs, Mic 1 + Mic 2) frame
by frame, so the ranges chosen for every tensor include the carried state
after gunshots, not just a silent start. The output keeps explicit
Quantize/DequantizeLinear nodes, which TensorRT reads directly with --int8.

Always compare INT8 against FP32 with evaluate/enhance before using it:
enhancement is sensitive to lost precision, and the GRUs usually stay FP.
"""
import argparse
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("onnx_fp32")
    ap.add_argument("--calib-dir", required=True)
    ap.add_argument("--frames", type=int, default=2000)
    ap.add_argument("--out")
    a = ap.parse_args()

    import onnx
    from onnxruntime.quantization import (CalibrationDataReader, QuantFormat, QuantType,
                                          quantize_static)
    from onnxruntime.quantization.shape_inference import quant_pre_process

    from enhance import load_mics
    from zeit.streaming import HOP, N_FFT, WIN, OnnxStreamer

    mics = onnx.load(a.onnx_fp32).graph.input[0].type.tensor_type.shape.dim[1].dim_value
    wavs = sorted(glob.glob(os.path.join(a.calib_dir, "*.wav")))
    if not wavs:
        sys.exit(f"no .wav files in {a.calib_dir}")

    # Record realistic (frame, state) inputs by running the FP32 model.
    feeds, st = [], OnnxStreamer(a.onnx_fp32, mics)
    for w in wavs:
        x = load_mics(w, None, mics); st.reset()
        for i in range(0, x.shape[1] // HOP * HOP, HOP):
            st.inbuf = np.concatenate([st.inbuf[:, HOP:], x[:, i:i + HOP]], axis=1)
            X = np.fft.rfft(st.inbuf * WIN, axis=-1)
            frame = np.stack([X.real, X.imag], -1)[None, :, :, None, :].astype(np.float32)
            feed = dict(frame=frame, conv_cache=st.conv, tra_cache=st.tra, inter_cache=st.inter)
            if i // HOP % 3 == 0:
                feeds.append({k: v.copy() for k, v in feed.items()})
            _, st.conv, st.tra, st.inter = st.sess.run(None, feed)
            if len(feeds) >= a.frames:
                break
        if len(feeds) >= a.frames:
            break
    print(f"  calibration frames: {len(feeds)} from {len(wavs)} file(s)")

    class Reader(CalibrationDataReader):
        def __init__(self):
            self.it = iter(feeds)

        def get_next(self):
            return next(self.it, None)

    pre = a.onnx_fp32.replace(".onnx", "_pre.onnx")
    quant_pre_process(a.onnx_fp32, pre)
    out = a.out or a.onnx_fp32.replace(".onnx", "_int8_qdq.onnx")
    quantize_static(pre, out, Reader(), quant_format=QuantFormat.QDQ,
                    activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
                    per_channel=True,
                    # ConvTranspose is left in FP: ONNX Runtime mis-sizes per-channel bias
                    # scales for grouped transposed convs (the two decoder upsamplers)
                    op_types_to_quantize=["Conv", "MatMul", "Gemm"])
    os.remove(pre)
    print(f"  -> {out}   ({os.path.getsize(out) / 1024:.0f} KB)")
    print("  next: compare with enhance.py against the FP32 file, then on the Jetson:")
    print(f"        bash jetson/build_engine.sh {os.path.basename(out)} int8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
