#!/usr/bin/env python3
"""selftest.py -- run the whole pipeline on generated audio in about a minute, CPU only.

    python selftest.py

Makes a tiny fake dataset (speech-like tones, bursts, hum, a 2-channel room
response), then: index -> train a few steps -> evaluate -> export ONNX with
parity checks -> streaming framing check -> prune -> INT8 quantise -> the
Jetson resampler. Must print ALL CHECKS PASSED before training on real data.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                                             # noqa: E402
import soundfile as sf                                         # noqa: E402

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}", flush=True)


def fake_data(root, rng):
    sr_s = [16000, 44100, 48000]
    for split_dir in ("train-clean-100", "dev-clean", "test-clean"):
        d = os.path.join(root, "speech", split_dir); os.makedirs(d)
        for k in range(6):
            sr = sr_s[k % 3]; t = np.arange(int(sr * 2.5)) / sr
            f0 = 110 + 60 * np.sin(2 * np.pi * 0.7 * t + k)
            ph = 2 * np.pi * np.cumsum(f0) / sr
            x = sum(np.sin(h * ph) / h for h in range(1, 8)) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t) ** 2)
            sf.write(os.path.join(d, f"s{k}.flac" if k % 2 else f"s{k}.wav"), 0.3 * x, sr)
    d = os.path.join(root, "noise"); os.makedirs(d)
    for k in range(9):
        sr = 16000; n = sr * 3
        if k % 3 == 0:
            x = np.zeros(n); x[rng.integers(0, n, 6)] = rng.standard_normal(6) * 5
            x = np.convolve(x, np.exp(-np.arange(800) / 150), "same")
        elif k % 3 == 1:
            x = np.sin(2 * np.pi * 90 * np.arange(n) / sr) + 0.2 * rng.standard_normal(n)
        else:
            x = np.cumsum(rng.standard_normal(n)); x -= np.convolve(x, np.ones(400) / 400, "same")
        sf.write(os.path.join(d, f"n{k}.wav"), 0.2 * x / np.max(np.abs(x)), sr)
    d = os.path.join(root, "rir"); os.makedirs(d)
    for k in range(3):
        L = 4000; t = np.arange(L)
        rir = rng.standard_normal((L, 2)) * np.exp(-t / 600)[:, None]
        rir[0] = 1.0
        sf.write(os.path.join(d, f"r{k}.wav"), rir * 0.5, 16000)


def main():
    rng = np.random.default_rng(0)
    tmp = tempfile.mkdtemp(prefix="zeit_selftest_")
    py = sys.executable
    try:
        data = os.path.join(tmp, "data"); fake_data(data, rng)
        idx = os.path.join(tmp, "index.jsonl")
        runs = os.path.join(tmp, "runs")
        ov = [f"data.root={data}", f"data.index={idx}", f"run.out_dir={runs}",
              "data.sources=[{name: librispeech, role: speech, path: speech, "
              "split: {train: [train-clean-100], val: [dev-clean], test: [test-clean]}}, "
              "{name: noise, role: noise, cls: impulsive, path: noise, split: {train: [''], val: [''], test: ['']}}, "
              "{name: rirs, role: rir, path: rir, split: {train: [''], val: [''], test: ['']}}]",
              "mix.speech_weights={librispeech: 1.0}", "mix.noise_class_weights={impulsive: 1.0}",
              "audio.segment_s=1.0", "data.val_items=4", "data.test_items=8",
              "train.items_per_epoch=8", "train.batch_size=4", "train.num_workers=0",
              "train.epochs=1", "train.eval_pesq_every=1", "mix.clip_prob=0.5", "mix.rir_prob=0.7"]
        cfg_path = os.path.join(HERE, "configs", "base.yaml")

        def run(args):
            r = subprocess.run([py, *args], cwd=HERE, capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

        code, out = run(["build_index.py", cfg_path, *ov])
        check("build_index", code == 0, "" if code == 0 else out[-800:])

        from zeit import config
        from zeit.data import DualMicMix, load_index
        cfg = config.load(cfg_path, ov)
        ds = DualMicMix(cfg, load_index(idx), "val", fixed=True, length=4)
        a1, b1, s1 = ds[2]; a2, b2, s2 = ds[2]
        check("fixed validation items are identical", bool((a1 == a2).all() and float(s1) == float(s2)))
        check("mixture shape (mics, samples)", tuple(a1.shape) == (2, 16000), str(tuple(a1.shape)))
        check("mixture finite", bool(np.isfinite(a1.numpy()).all()))

        code, out = run(["train.py", cfg_path, *ov, "--device", "cpu"])
        check("train (1 epoch, tiny)", code == 0 and "best.pt" in out, "" if code == 0 else out[-1500:])
        ckpts = [os.path.join(dp, f) for dp, _, fs in os.walk(runs) for f in fs if f == "best.pt"]
        if not ckpts:
            raise SystemExit("no checkpoint — stopping")
        ck = ckpts[0]

        code, out = run(["evaluate.py", ck, "--items", "8", "--device", "cpu"])
        check("evaluate", code == 0 and os.path.exists(os.path.join(os.path.dirname(ck), "eval", "summary.json")),
              "" if code == 0 else out[-1500:])

        onnx_path = os.path.join(os.path.dirname(ck), "gtcrn_stream.onnx")
        code, out = run(["export_onnx.py", ck, "--out", onnx_path])
        check("export ONNX + parity (stream==full, ORT==torch)", code == 0 and "verified" in out,
              "" if code == 0 else out[-1500:])

        # framing: with an identity "model", the streamer must return the input delayed by one hop
        from zeit.streaming import HOP, OnnxStreamer
        st = OnnxStreamer.__new__(OnnxStreamer); st.mics = 2

        class Echo:
            def run(self, _, feed):
                return [feed["frame"][:, 0], feed["conv_cache"], feed["tra_cache"], feed["inter_cache"]]
        st.sess = Echo(); st.reset()
        x = rng.standard_normal((2, HOP * 40)).astype(np.float32)
        y = np.concatenate([st.process(x[:, i:i + HOP]) for i in range(0, x.shape[1], HOP)])
        err = float(np.max(np.abs(y[HOP * 2:] - x[0, HOP:-HOP])))
        check("streaming STFT/ISTFT reconstructs perfectly", err < 1e-4, f"max err {err:.1e}")

        wav = os.path.join(tmp, "noisy.wav")
        mics, _, _ = ds[0]
        sf.write(wav, mics.numpy().T, 16000)
        code, out = run(["enhance.py", onnx_path, wav, "-o", os.path.join(tmp, "clean.wav")])
        check("enhance with ONNX", code == 0, "" if code == 0 else out[-800:])

        code, out = run(["prune.py", ck, "--amount", "0.3"])
        check("prune", code == 0 and "pruned" in out, "" if code == 0 else out[-800:])

        calib = os.path.join(tmp, "calib"); os.makedirs(calib)
        for k in range(2):
            m, _, _ = ds[k]; sf.write(os.path.join(calib, f"c{k}.wav"), m.numpy().T, 16000)
        code, out = run(["quantize_onnx.py", onnx_path, "--calib-dir", calib, "--frames", "40"])
        q = onnx_path.replace(".onnx", "_int8_qdq.onnx")
        check("INT8 QDQ quantisation", code == 0 and os.path.exists(q), "" if code == 0 else out[-1500:])

        sys.path.insert(0, os.path.join(HERE, "jetson"))
        from realtime import BLOCK, FS_IO, Resampler
        rs = Resampler(1)
        t = np.arange(BLOCK * 30) / FS_IO
        sig = np.sin(2 * np.pi * 1000 * t)
        ys = np.concatenate([rs.up(rs.down(sig[None, i:i + BLOCK])[0]) for i in range(0, len(sig), BLOCK)])
        amp = float(np.sqrt(2 * np.mean(ys[BLOCK * 5:] ** 2)))
        check("Jetson 48k<->16k resampler keeps a 1 kHz tone", abs(amp - 1) < 0.05, f"gain {amp:.3f}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = all(RESULTS)
    print(f"\n  {'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}  ({sum(RESULTS)}/{len(RESULTS)})\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
