# Tech stack

Three places code runs, and one rule for each:

| Where | Language / tool | Rule |
|---|---|---|
| **ADAU1787 DSP** (Lane A) | SigmaStudio graphical design, loaded by the STM32 | Everything that must beat sound to the ear |
| **STM32** (Lane A manager) | C (STM32Cube) | Control, boot-loading, adaptation — never in the audio path |
| **Jetson Orin Nano Super** (Lane B) | C++17 for the real-time engine, TensorRT for the model; Python for the first live runner | Everything with a tens-of-milliseconds deadline |
| **Training machine** (college supercomputer) | Python + PyTorch | Everything offline; never runs on the device |

**The boundary between training and the device is one ONNX file.** PyTorch
produces it; TensorRT consumes it; nothing else crosses.

The architecture these serve is in [`architecture.md`](architecture.md); the
parts in [`../../synthetic_generator/HARDWARE.md`](../../synthetic_generator/HARDWARE.md).

---

## 1. Lane A — ADAU1787 + STM32

| # | What | For | Status |
|---|---|---|---|
| 1 | **SigmaStudio** (Analog Devices, free) | Designing the DSP program graphically: filters, limiters, mixers, detectors (A1–A11) | Not started |
| 2 | **FastDSP blocks** | Biquads, limiters, volume, mixing at up to 768 kHz — hear-through, ANC filters, limiters | Not started |
| 3 | **SigmaDSP core** | Envelopes (A3), crack guard (A4), clip flags (A1), mode parameter sets | Not started |
| 4 | **STM32CubeIDE, C** | STM32 firmware | Not started |
| 5 | **Boot loader (STM32)** | Writes the SigmaStudio-exported program into the ADAU over I²C at power-on (unless the eval board self-boots — check UG-1532) | Not started |
| 6 | **UART protocol (STM32 ↔ Jetson)** | Modes down, PTT state and crack events up — defined in `architecture.md` §8 | Defined; not coded |
| 6b | **PTT (STM32)** | Reads the PTT button, drives the radio's PTT optocoupler | Not started |
| 7 | **FxLMS (STM32)** | Phase 2 adaptation (A8), mic data over SAI (I²S/TDM) | Not started |

Build order for Lane A: hear-through + limiters → fixed ANC in both ears →
boot loading from the STM32 → modes over UART → adaptation.

---

## 2. Lane B — Jetson

### 2.1 Libraries

| # | What | For | Licence | Status |
|---|---|---|---|---|
| 8 | **JetPack** (NVIDIA) | Ubuntu, CUDA, cuDNN, **TensorRT** on the Jetson | NVIDIA | Install on arrival |
| 9 | **TensorRT** | Runs the model: ONNX → engine, FP16 then INT8. The PS names it | proprietary (free) | Scripts built (`training/jetson/build_engine.sh`) |
| 10 | **ONNX Runtime (GPU, Jetson build)** | Fallback runner, and the TensorRT execution provider used by the Python live runner | MIT | Runner built (`training/jetson/realtime.py`) |
| 11 | **ALSA** | Audio in/out through the UMC404HD | LGPL | — |
| 12 | **C++17 + CMake** | The real-time engine (blocks B1–B11, R1–R5) | — | Not started |
| 13 | **PFFFT** | FFT for STFT/ISTFT in the C++ engine. **Not FFTW** — GPL or paid | BSD-style | Not started |
| 14 | **Eigen** | AR / Levinson-Durbin for BMRI (B6) | MPL2 | Not started |
| 15 | **doctest** | Unit tests, parity test, real-time safety test | MIT | Not started |

### 2.2 Hand-written — no library does these

| Block | What |
|---|---|
| B2 | Impulse detector (peak / kurtosis / high-frequency energy at 48 kHz) |
| B3 | Robust normalisation (percentile / FLOM — never RMS) |
| B5 | Scene classifier → modes and γ / β |
| B6 | BMRI impulse repair |
| B8, B9 | Merge and voice guard |
| B10 | Residual LMS (optional) |
| R1–R5 | Radio receive: voice detect, hiss removal, AGC, speech EQ, limiter |
| — | Lock-free ring buffers, 48 ↔ 16 kHz resamplers, UART link to the STM32 (PTT is keyed by the STM32) |

### 2.3 Two stages of the live runtime

| Stage | What | Why |
|---|---|---|
| **1. Python runner** — `training/jetson/realtime.py` | ONNX Runtime with the TensorRT provider; capture → model → output | Exists now; proves the model, TensorRT and the audio path on the Jetson quickly |
| **2. C++ engine** | Same blocks with strict real-time rules | Deterministic worst-case timing; the deliverable engine |

The Python runner takes 3 input channels (boom, reference, throat; `--in-ch 1 2 3`)
and passes the radio receive channel (`--rx-ch 4`) through to UMC output 2.

---

## 3. Training machine — Python (offline)

| # | What | For | Status |
|---|---|---|---|
| 16 | **Python 3.11 / 3.12** | Everything offline (PyTorch does not yet support every newer Python) | — |
| 17 | **PyTorch + torchaudio** | Model, training | Framework built (`training/`) |
| 18 | **numpy, scipy** | Mixing, augmentation, resampling | Built |
| 19 | **soundfile** | Reading WAV / FLAC corpora for training | Used by `training/` only |
| 20 | **torch.onnx** | Streaming ONNX export with parity checks | Built (`export_onnx.py`) |
| 21 | **onnxruntime (+ quantization tools)** | Parity checks, INT8 QDQ calibration | Built |
| 22 | **pesq, pystoi** | PS metrics | Integrated; `pesq` needs a C compiler on Windows |
| 23 | **DNSMOS** | SIG / BAK split so over-suppression is visible | To add |
| 24 | **TensorBoard** | Training curves | Integrated |
| 25 | **our `wavio.py`** | WAV I/O for the range toolkit (no native library, so nothing can fail in the field) | Built |

The range toolkit (`data_collection/`) deliberately avoids `soundfile`; the
training framework uses it because it reads FLAC corpora and never runs in the field.

### Not using, deliberately

| What | Why not |
|---|---|
| FFTW | GPL or commercial licence |
| librosa | Heavy; numpy + scipy cover it |
| An experiment-tracking service | Every run already writes JSON, CSV and TensorBoard logs |
| Aux-IVA | Removed from the architecture: underdetermined with 2–3 mics; the throat mic does its job |

---

## 4. Audio settings — locked

| Setting | Value | Why |
|---|---|---|
| Capture | 48 kHz, 24-bit, 768-sample blocks (16 ms) | UMC404HD native rate; clean 3:1 resampling |
| Model rate | **16 kHz** | GTCRN's native rate; radio voice is narrowband anyway |
| STFT | **512-point FFT, 256 hop, √Hann** (32 ms window, 16 ms hop) | Keeps GTCRN's band layout and published size valid |
| Compute deadline | **16 ms per frame**, worst case | Miss it and the output underruns (a click) |
| Mouth-to-radio | ≈ 70–85 ms (ESTIMATE) | ITU-T G.114: ≤ 150 ms one-way is transparent |

Report the **99th-percentile** frame time, not the mean. A mean of 3 ms with
occasional 20 ms spikes fails a 16 ms deadline, and the mean hides it.

---

## 5. Real-time rules (C++ engine, audio thread)

- No allocation — every buffer preallocated at start-up
- No locks — lock-free ring buffer between the audio thread and processing
- No exceptions, no I/O, no logging in the audio path
- No `std::vector` growth, no `std::string`, no `new`

```
  audio thread        (real-time priority)   ALSA read/write, 768 samples, ring buffers
        │
  processing thread   (high priority)        B1–B11 and R1–R5, must finish inside 16 ms
        │
  control thread      (normal)               UART to STM32 (modes, PTT state), logging, live display
```

Lane A is not on these threads at all — it runs on the ADAU1787.

---

## 6. The boundary — and the parity test

```
   PyTorch (train.py) ──export_onnx.py──► gtcrn_stream.onnx ──build_engine.sh──► TensorRT engine (Jetson)
```

The silent failure: the device computes slightly differently from training
(FFT scaling, window, band edges, normalisation). Nothing crashes; the model
just performs worse. The guard is a **stage-by-stage parity test**:

| Check | Status |
|---|---|
| Streaming model = whole-clip model | MEASURED ≤ 6×10⁻⁸ (3-input) |
| ONNX Runtime = PyTorch streaming | MEASURED ≤ 5×10⁻⁸ (3-input) |
| Streaming STFT/ISTFT reconstruction | MEASURED 4.8×10⁻⁷ |
| TensorRT FP16 / INT8 vs FP32 | On the Jetson — to do |
| C++ engine vs Python, every stage | With the C++ engine — to do |

---

## 7. Repository layout

```
Zeit_at_SIH/
  data_collection/      Python — range toolkit (built)
  synthetic_generator/  Python — corpus download, metrics (IRT, WLPS), experiments, HARDWARE.md
  training/             Python — the neural network framework (built)
      zeit/               model, data mixing, augmentation, losses, metrics, streaming
      configs/            base.yaml (main run), sanity_voicebank.yaml
      train.py  evaluate.py  export_onnx.py  quantize_onnx.py  prune.py  enhance.py  selftest.py
      jetson/             build_engine.sh, realtime.py (live runner)
  docs/                 documentation (this folder)
  handbook/             evaluator-facing HTML pages
  engine/               C++ — the real-time Lane B engine (to build)
      src/  00_core/ ring_buffer.h, config.h (16 kHz, 512, 256)
            01_io/   alsa_io.cpp, resample.cpp
            02_lane_b/ detect.cpp, normalise.cpp, stft.cpp, classify.cpp, bmri.cpp,
                       infer_trt.cpp, merge.cpp, guard.cpp, lms.cpp
            03_rx/   rx_chain.cpp (R1–R5)
            04_link/ uart_stm32.cpp  (PTT lives in the STM32 firmware)
      tests/ parity_test.cpp, rt_safety_test.cpp
  firmware/             C — STM32 (to build): boot loader, UART, modes, PTT, FxLMS
  dsp/                  SigmaStudio projects for the ADAU1787 (to build)
```

---

## 8. Measuring on the actual hardware

| Number | How |
|---|---|
| ms per frame (Lane B) | Worst case and 99th percentile over a long run; `realtime.py` prints both |
| TensorRT engine latency | `build_engine.sh` (trtexec percentiles) |
| **Watts** (Jetson) | `tegrastats` power rails; an inline DC meter if an independent figure is wanted |
| ANC and hear-through (Lane A) | Mannequin ear mic (H22) on UMC in 4, system on vs off |
| Peak at the ear | Mannequin + high-SPL measurement, against 140 dBP |

---

## 9. Build order

| Step | What | Needs |
|---|---|---|
| 1 | VoiceBank-DEMAND sanity run (PESQ ≈ 2.87) | Supercomputer |
| 2 | 3-input data path (done, simulated throat) + real throat pairs + B3 + full training | Step 1 |
| 3 | Jetson: JetPack, UMC404HD recording, TensorRT engine, `realtime.py` | Hardware |
| 4 | Headset build + tests | Hardware |
| 5 | SigmaStudio: hear-through + limiters, then fixed ANC | ADAU board |
| 6 | STM32: boot load, UART modes | Steps 3, 5 |
| 7 | Radio receive chain R1–R5 and PTT | Steps 3, 4 |
| 8 | C++ engine with parity tests | Step 3 |
| 9 | Adaptive ANC (FxLMS) | Step 6 |

---

## 10. Decisions, and what would change them

| Decision | Reason | Revisit if |
|---|---|---|
| Jetson Orin Nano Super for Lane B | PS names Jetson and TensorRT | TensorRT cannot run the GRU layers — then ONNX Runtime CUDA on the same board |
| ADAU1787 for Lane A | Low-latency analog-in → DSP → analog-out path built for ANC headsets | FastDSP capacity insufficient for two ears — shorten ANC filters |
| 16 kHz, 32 / 16 ms | GTCRN's native settings; published sizes stay valid | Latency must drop below ~50 ms |
| Fixed ANC before adaptive | Lower risk; commercial headsets often ship fixed ANC | Fixed ANC proves inadequate on real noise |
| Python runner before C++ engine | Proves the chain on the Jetson quickly | Timing jitter in Python exceeds the 16 ms deadline |
| PFFFT over FFTW | Licence | — |
