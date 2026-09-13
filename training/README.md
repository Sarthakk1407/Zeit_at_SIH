# training/

The Lane B model: **train in PyTorch → export ONNX → run with TensorRT on the
Jetson.** One trained network (GTCRN, dual microphone); everything else in the
11-block chain is hand-written code in the C++ engine.

```
PyTorch  ──train.py──►  best.pt  ──export_onnx.py──►  gtcrn_stream.onnx
                                                            │  (copy to the Jetson)
                                                            ▼
                                  jetson/build_engine.sh ─► TensorRT engine ─► jetson/realtime.py
```

**Start with `python selftest.py`.** It runs the entire pipeline on generated
audio in about a minute on CPU and must print `ALL CHECKS PASSED`.

## The model

| | |
|---|---|
| Network | GTCRN (Rong et al., ICASSP 2024), re-implemented, with Mic 2 added as input channels |
| Parameters | **24,389** dual-mic · **23,669** single-mic (the paper reports 23.7 K — this matches) |
| Input | Complex STFT of Mic 1 **and** Mic 2: magnitude, real, imaginary |
| Output | A complex ratio mask applied to **Mic 1's noisy spectrum** (H-GTCRN's finding) |
| Structure | ERB band merging (65 low bins kept, 192 high bins → 64 bands), subband feature extraction, grouped temporal convolutions with attention, dual-path grouped GRUs (across frequency and across time) |
| Audio | **16 kHz, 32 ms window, 16 ms hop** — GTCRN's native settings |
| Latency | 32 ms algorithmic + ~2 ms resampling + audio buffers. Well inside the ~150 ms one-way delay voice links tolerate |
| Causal | Yes. Every time-direction layer looks only backwards, so the model runs frame by frame |

> **This resolves the rate conflict** noted in `docs/01-system/architecture.md`
> §7 and `synthetic_generator/MODEL_VALUES.md` §6: the model uses GTCRN's
> published 16 kHz / 32 ms / 16 ms settings rather than 48 kHz / 20 ms /
> 10 ms, so its band layout and parameter count stay valid. The docs' 25.3 ms
> Lane B figure needs updating to match.

## The data — mixed fresh, never stored

Your corpora are single-microphone, but the model needs two. `zeit/data.py`
builds every training example on the fly:

```
Mic 1  = speech                            + g · noise_at_Mic1
Mic 2  = tiny speech leak (−45…−25 dB)     + g · noise_at_Mic2
target = clean speech
```

- **noise_at_Mic2** is the same noise reaching a point ~20 cm away: two channels
  of a real multichannel room response when one is available, otherwise a
  ±0.6 ms delay plus a frequency-dependent head shadow.
- **SNR**: half the time −15…0 dB (the gunfire regime), half 0…+20 dB.
- **Speech**: 80 % LibriSpeech, 20 % Lombard GRID (people talking in noise).
- **Noise classes**: impulsive (Zenodo, Cadre) 40 %, military (MAD, NOISEX-92)
  30 %, stationary (DEMAND, MUSAN) 20 %, urban (UrbanSound8K, ESC-50) 10 %, plus
  **α-stable structured bursts** 25 % of the time, including α < 0.5.
- **Clipping** on either mic 25 % of the time: the input-side saturation nobody models.
- **Room responses** from OpenSLR28, 50 % of the time.
- **Our own 44 range events are test-only.** They are the reference; they never train.

Validation and test items are seeded by index, so they are identical in every
run. All of these settings are in `configs/base.yaml`.

## Files

| File | What it does |
|---|---|
| `selftest.py` | Whole pipeline on fake audio, CPU, ~1 minute. Run first |
| `build_index.py` | Scans the data drive once, writes `data_index.jsonl` |
| `train.py` | Trains. Writes `runs/<name>-<confighash>/best.pt`, `last.pt`, `history.json`, TensorBoard logs |
| `evaluate.py` | Scores a checkpoint on the fixed test set: SNR out, ΔSNR, SI-SNR, PESQ, STOI **per input-SNR bucket**, and where each PS target is first met |
| `export_onnx.py` | Checkpoint → streaming ONNX. Refuses to finish unless streaming == whole-clip and ONNX == PyTorch to 1e-4 |
| `enhance.py` | Cleans a recorded 2-channel WAV with a `.pt` or `.onnx` |
| `prune.py` | Global magnitude pruning; fine-tune afterwards with `train.py --init` |
| `quantize_onnx.py` | INT8 (QDQ) ONNX, calibrated on real noisy recordings |
| `jetson/build_engine.sh` | On the Jetson: ONNX → TensorRT engine, plus a per-frame latency benchmark |
| `jetson/realtime.py` | On the Jetson: live mics in → cleaned voice out, ENTER toggles the model on/off, prints p99 frame time |
| `configs/base.yaml` | The main experiment: every dataset folder, mixing, loss and training setting |
| `configs/sanity_voicebank.yaml` | Single-mic GTCRN on VoiceBank-DEMAND, to check PESQ ≈ 2.87 first |
| `zeit/` | The library: `model.py`, `data.py`, `augment.py`, `losses.py`, `metrics.py`, `audio.py`, `streaming.py`, `config.py` |

## Step by step

### 0. Set up the training machine

A GPU is needed; the model is tiny, so an RTX 3060-class card, Kaggle's free
T4/P100 or a rented cloud GPU is plenty. Use **Python 3.11 or 3.12**.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
python selftest.py
```

### 1. Prove the code on a known benchmark

Download VoiceBank-DEMAND, set its four folders in
`configs/sanity_voicebank.yaml`, then:

```bash
python train.py configs/sanity_voicebank.yaml
python evaluate.py runs/sanity_voicebank_mono-*/best.pt
```

PESQ should land near the paper's **2.87**. If it is far off, fix that before
anything else — every later number depends on this code being right.

### 2. Index your data

Set `data.root` in `configs/base.yaml` to where the drive is mounted, then:

```bash
python build_index.py configs/base.yaml
```

Folders that are missing are skipped with a warning. It prints the file count
per role and split.

### 3. Train

```bash
python train.py configs/base.yaml
tensorboard --logdir runs
```

Anything can be overridden without editing the file:

```bash
python train.py configs/base.yaml train.batch_size=16 train.num_workers=4
python train.py configs/base.yaml --resume runs/gtcrn_dualmic-XXXX/last.pt
```

Training stops early when validation SI-SNR has not improved for 20 epochs.

### 4. Evaluate

```bash
python evaluate.py runs/gtcrn_dualmic-XXXX/best.pt
```

Report the `by_snr.csv` curves, not a single average. "SNR > 15 dB" is reported
both ways — output SNR and improvement — because the PS does not say which.

### 5. (Optional) prune and fine-tune

```bash
python prune.py runs/gtcrn_dualmic-XXXX/best.pt --amount 0.3
python train.py configs/base.yaml train.epochs=30 train.lr=2e-4 --init runs/gtcrn_dualmic-XXXX/pruned_30.pt
```

### 6. Export to ONNX

```bash
python export_onnx.py runs/gtcrn_dualmic-XXXX/best.pt
```

The streaming model's inputs and outputs:

| Name | Shape | Meaning |
|---|---|---|
| `frame` | (1, 2, 257, 1, 2) | One noisy STFT frame, both mics |
| `conv_cache` | (1, 6, 16, 10, 33) | Past frames the causal convolutions need |
| `tra_cache` | (6, 1, 16) | Attention GRU states |
| `inter_cache` | (4, 33, 8) | Time-direction GRU states |
| `enhanced` | (1, 257, 1, 2) | Mic 1's clean frame |
| `*_out` | as above | Feed back in with the next frame |

### 7. (Optional) INT8

Put a few dozen real 2-channel noisy WAVs in a folder:

```bash
python quantize_onnx.py runs/gtcrn_dualmic-XXXX/gtcrn_stream.onnx --calib-dir calib_wavs/
```

Compare against FP32 with `enhance.py` and your ears before trusting it. The
decoder's two transposed convolutions stay in floating point (an ONNX Runtime
quantiser limitation).

### 8. On the Jetson

Copy `gtcrn_stream.onnx` and the `jetson/` and `zeit/` folders over. TensorRT and
CUDA come with JetPack; add `onnxruntime-gpu` (the Jetson wheel), `sounddevice`,
`numpy`, `scipy`, `onnx`.

```bash
cd jetson
bash build_engine.sh ../gtcrn_stream.onnx fp16          # builds the engine, prints latency
python3 realtime.py --onnx ../gtcrn_stream.onnx --list-devices
python3 realtime.py --onnx ../gtcrn_stream.onnx --device "UMC404HD" --trt-fp16
```

Mic 1 on interface input 1, Mic 2 on input 2 (change with `--in-ch`). Press
**ENTER** to switch the model on and off. On exit it prints mean, p99 and max
frame time — quote the p99, not the mean.

## What is not here yet

- **Blocks 2, 5, 6, 8, 9, 10** (Aux-IVA, kurtosis classifier, BMRI, deep
  filtering, voice guard, residual LMS) — these are the C++ engine. Deep
  filtering will later become a second output head on this same network.
- **Structured pruning** — `prune.py` is unstructured; zeros do not cut
  TensorRT latency by themselves.
- **DNSMOS** — add Microsoft's DNSMOS ONNX model to `zeit/metrics.py` so
  over-suppression (SIG vs BAK) is visible.
- **Verified learning on real data.** The self-test proves the pipeline runs
  end to end and that export is faithful; it does not prove the model reaches
  the PS targets. That is what steps 1 and 4 are for.
