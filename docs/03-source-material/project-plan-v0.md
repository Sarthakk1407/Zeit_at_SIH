# SIH 26052 — AI/ML Adaptive Noise Cancellation
## Team ZEIT v.1.0 — architecture, workflow and delivery plan

---

# 1. System architecture

## 1.1 The two-lane split

The single most common mistake on this problem statement is treating "ANC" as one system. It is two systems with wildly different latency budgets.

| | Lane A — cancellation | Lane B — enhancement |
|---|---|---|
| **Signal path** | Reference mic → speaker → ear | Boom mic → radio uplink |
| **Goal** | Protect the wearer's hearing | Make outgoing speech intelligible |
| **Latency budget** | Sub-millisecond | 20–40 ms |
| **Algorithm** | FxLMS + secondary path estimation | Neural denoiser |
| **Runs on** | DSP / MCU | Same MCU or small SoC |
| **Owner** | Hardware (friend) | Software (you) |

A neural network cannot live inside Lane A on affordable embedded hardware. The anti-noise must be emitted before the acoustic wave physically arrives at the ear — that is microseconds of headroom, not milliseconds. Any team claiming a transformer does their active cancellation has not measured their own latency.

State this split explicitly on your architecture slide. It reads as engineering maturity and it is a free differentiator.

## 1.2 Hybrid rationale

- Lane A (FxLMS) handles **low-frequency continuous** noise — engine, rotor, generator, vehicle rumble. This is what classical ANC is genuinely good at.
- Lane B (neural) handles **broadband, impulsive and non-stationary** noise in the speech channel — gunshots, blasts, transients. This is what classical DSP fails at, and it is exactly the gap the problem statement calls out.

The two lanes are complementary, not redundant. Say so.

---

# 2. Dataset architecture

```
                RAW SOURCES
   ┌──────────────┬──────────────┬──────────────┐
   │ Clean speech │ Noise corpus │ Acoustic     │
   │ (download)   │ (mixed)      │ paths        │
   └──────┬───────┴──────┬───────┴──────┬───────┘
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 ┌───────────────┐
                 │ MIXING ENGINE │   ← config-driven, seeded
                 │ SNR / RIR /   │
                 │ alignment     │
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ DEVICE CHAIN  │   ← calibrated from range data
                 │ clip / AGC /  │
                 │ vocoder       │
                 └───────┬───────┘
                         ▼
                  TRAINING PAIRS
                         │
                         ▼
                    MODEL  ────►  eval on HELD-OUT REAL RECORDINGS
```

Everything is generated **on the fly** at train time from a seeded config. No pre-rendered mixture files. This keeps the repo small, makes every experiment reproducible from a config hash, and lets you resample SNR/RIR per epoch.

---

# 3. Where each piece of data comes from

## 3.1 Clean speech (download)

| Corpus | What | Why |
|---|---|---|
| LibriSpeech | ~1000 h read English | Bulk volume |
| VCTK | 110 speakers, accented English | Speaker diversity |
| EARS | Studio quality, expressive | High-fidelity targets |
| DNS5 LibriVox subset | Filtered clean speech | Standard SE baseline |
| **IndicTTS / SPRING-INX** | **Indian languages** | **Evaluators speak Hindi/Indian English** |
| Common Voice (Hindi) | Crowd-sourced Hindi | Accent robustness |
| **Lombard GRID** | **54 speakers, neutral + Lombard pairs** | **Critical — see below** |

**Lombard is not optional.** Speakers in high noise raise pitch, loudness and shift spectral tilt. Systems trained on neutral speech lose roughly 5 dB when tested on Lombard speech, and the gap persists even after level normalisation. Lombard GRID recorded each of its 54 speakers in both conditions, with the Lombard condition induced by 80 dB SPL speech-shaped noise over headphones. Aim for **≥20% Lombard content** in your training mix.

**Boom-mic emulation:** clean corpora are recorded at 30 cm. A headset boom mic sits at 2–5 cm. Apply a low-shelf boost (proximity effect), light saturation, and occasional plosive bursts before mixing.

## 3.2 Noise (download + record + synthesise)

**Impulsive — download:**

| Source | Contents | Access |
|---|---|---|
| Gunshot Audio Forensics Dataset (Cadre) | ~10,000 recordings, 20 firearms, 20 positions each, 4 devices | cadreforensics.com/audio — free, register |
| Kabealo multi-orientation set | 2,148 files, 4 firearms, time-synced, CSV with per-shot timestamps | Open access |
| Free Firearm Sound Library | Wide firearm variety | CC0 — no restrictions |

**Impulsive — synthesise:** your Friedlander generator (Section 5).

**Impulsive — measure:** your range session (Section 4).

**Non-stationary and stationary — download:**

| Corpus | Contents |
|---|---|
| MUSAN | Music, speech, general noise |
| DEMAND | 18 real environments, multichannel |
| FSD50K | 200 sound classes incl. vehicles, engines |
| WHAM! | Real ambient recordings |
| AudioSet (filtered) | Helicopter, aircraft, machinery classes |

Extract and tag: helicopter rotor, tracked/wheeled vehicle, generator hum, wind, radio hiss, alarm/siren.

**Keep civilian noise in the mix.** A model trained only on gunshots will fail on everything else. Target roughly 35% impulsive, 35% non-stationary, 30% stationary.

## 3.3 Acoustic paths

| Source | What | Use |
|---|---|---|
| **iks\|PANDAR** (RWTH Aachen) | Measured primary, secondary and feedback paths for ANC headphones | Lane A simulation before hardware exists |
| openSLR26 / openSLR28 | Room impulse responses | Indoor reverb augmentation |
| **Your own headset** | Measured IRs from the actual prototype | **The USP — Section 9** |
| Your range IR | Measured on-site | Places synthetic blasts in a real outdoor space |

For outdoor gunshot propagation do **not** use room RIRs. Model direct path + ground reflection + atmospheric absorption analytically.

---

# 4. Range session — one visit

Full checklist is in `range_field_checklist.md`. Summary of priorities:

**Tier 0 (do first, 20 min):** calibration tone with SPL reference, noise floor, mic response sweep, **range impulse response sweep**, geometry with photos, weather log.

The range IR is the highest-value artefact of the whole trip. With it you can convolve unlimited synthetic blasts into that exact acoustic space.

**Tier 1:** impulsive sources across an energy range. Given age/access constraints, the realistic source set is:

| Source | Peak SPL (approx) | Value |
|---|---|---|
| Balloon pop | ~110 dB | Free, uniform radiation, N-wave |
| Spring air rifle | ~100 dB @ 60 cm | Low end of scale |
| PCP air rifle | 110–120 dB | Plus possible supersonic pellet crack |
| **Firecrackers (3 sizes)** | up to ~125 dB | **Real explosive charge, gives energy scaling axis** |
| **Starter pistol / blank gun** | ~130–140 dB | **Real cartridge, real muzzle blast — get this** |
| Whip crack | — | Genuine sonic boom / shock wave |

For reference, real firearms sit at 135–150 dB (.22 LR), 160–165 dB (9 mm), 165–170 dB (5.56). You will not reach these. That is fine — see Section 6.

**Tier 2:** mechanical action sounds close-miked separately — bolt cycling, brass ejection, trigger, magazine. A gunshot event is muzzle blast plus shock wave plus mechanical action plus environmental reflections; almost nobody records the mechanical layer, and it is what makes synthetic shots sound real rather than like a bare pressure pulse.

**Tier 3:** range ambience, and speech recorded during live impulsive noise — your most valuable single file.

**Split fit/holdout at the range, before you leave.** Fit set ≈30%, holdout ≈70%. The holdout is never opened until the generator is frozen.

---

# 5. Synthetic generation

## 5.1 Blast synthesiser

Core model — Friedlander waveform:

```
p(t) = Ps · (1 − t/T₀) · e^(−b·t/T₀)
```

- `Ps` — peak overpressure
- `T₀` — positive phase duration
- `b` — decay coefficient

Published anchors for firearms: .22 pistol ≈146 dB @ 1 m with peak near 750 Hz; .357 Magnum ≈155 dB with peak near 400 Hz. Peak frequency shifts down as calibre grows.

## 5.2 Full generation chain

```
1. Sample source params (Ps, T₀, b) from calibre/charge distribution
2. Generate Friedlander waveform
3. Apply directivity correction by azimuth
4. Apply spherical spreading over distance
5. Apply atmospheric absorption (temp, humidity dependent)
6. Add ground reflection (delay from geometry, surface coefficient)
7. Convolve with range IR or outdoor model
8. Layer mechanical action sounds (recorded, Tier 2)
9. Pass through device chain
```

Steps 3–6 are where most naive implementations stop at step 2 and produce something that sounds synthetic.

## 5.3 Device chain

Firearms exceed 154 dB SPL at 3 m; consumer microphones saturate around 120–130 dB. **Your field microphone will clip.** Model it:

- Hard and soft clipping at configurable thresholds
- AGC with attack/release pumping
- Microphone self-noise floor
- ADC quantisation
- Optional low-bitrate vocoder (MELP/AMBE class) simulating the radio link downstream of the denoiser

Calibrate the clipping model against your deliberately-clipped range recordings. That is what makes this defensible rather than guessed.

---

# 6. Validation protocol

## 6.1 The honest reframing

You are not claiming *"our synthetic gunshots match real gunshots."* You cannot support that with an air rifle.

You are claiming:

> *"We built a physics-based blast synthesis pipeline and validated it against N measured impulsive sources spanning ~45 dB of peak level. Prediction error stayed within ±X dB across that range. Because the underlying model is energy-scaled, this supports extrapolation to firearm-scale sources, which we validated separately in shape and spectrum against published real-firearm recordings."*

This is a stronger methodology story than "we fired one gun once," and it is defensible under questioning.

## 6.2 Four validation levels

| Level | Compares | Method | Target |
|---|---|---|---|
| **1. Physical** | Ps, T₀, b, rise time | Fit Friedlander to real and synthetic, compare parameter distributions | Ps ±2 dB, T₀ ±15% |
| **2. Spectral** | 1/3-octave band SEL, 63 Hz–8 kHz | Band-wise error curve | ±3 dB per band |
| **3. Statistical** | Kurtosis, crest factor, distribution overlap | KS test, MMD, Fréchet Audio Distance | FAD near the real-vs-real floor |
| **4. Task-level** | Model performance | Cross-training ablation | Within 1–2 dB of real-trained |

**Level 3 requires a floor.** Split your real recordings into two random halves and compute FAD(real, real). That is the noise floor — two genuine sets never match perfectly. Report FAD(synth, real) against that floor. A FAD number without a floor is meaningless.

## 6.3 Level 4 — the money chart

Train four models, test all four on your **held-out real recordings**:

| Training data | Expected | Proves |
|---|---|---|
| Civilian noise only | Worst | The domain gap is real |
| **Synthetic only** | **Near ceiling** | **Synthetic data has standalone value** |
| Synthetic + public real | Best practical | Recommended production config |
| Real only | Ceiling | Upper bound |

If "synthetic only" lands within 1–2 dB of "real only" and 5+ dB above "civilian only," the argument is closed.

## 6.4 Energy-scaling chart

X-axis: measured peak SPL (95 → 140 dB). Y-axis: model prediction error (dB). One point per source type. If all points sit in a ±2 dB band, draw a dotted extrapolation to firearm range. This single figure is your strongest visual.

## 6.5 Anti-fraud discipline

- Range holdout is **never** trained on
- Generator parameters come **only** from the fit set
- Freeze the generator with a git tag before touching holdout
- Report the mismatches you find. "Our generator overestimates by 4 dB above 2 kHz" reads as honest science. "Everything matched perfectly" reads as untested.

---

# 7. Novel metrics — the cheapest USP available

PESQ and STOI average over the whole utterance. A gunshot destroys ~200 ms of speech, but in a 10-second clip the average barely moves. **The standard metrics hide exactly the damage this problem statement is about.**

Propose two metrics:

**IRT — Impulse Recovery Time**
Milliseconds after impulse onset until band-wise SNR returns to 90% of its pre-impulse level. Measures how fast the denoiser recovers.

**WLPS — Words Lost Per Shot**
Run ASR on the enhanced output. Count word errors falling inside the impulse window, normalised per impulse event.

Both are under ~50 lines of code. Report standard metrics **and** these. The narrative — *"we showed existing metrics under-report impulsive damage, so we propose two that don't"* — is a genuine research contribution, and it is far more memorable to a judging panel than another dataset.

---

# 8. Model selection

## 8.1 Candidates with real numbers

| Model | Params | MACs/s | WB-PESQ (VCTK-DEMAND) | Verdict |
|---|---|---|---|---|
| RNNoise | 0.06 M | 0.04 G | 2.34 | Too weak; useful as a classical baseline |
| **GTCRN** | **23.7 K** | **39.6 M** | **2.87** | **Primary pick** |
| UL-UNAS | ~0.05 M | 35 M | GTCRN +0.20 | Stretch goal, same MAC budget |
| LiSenNet | — | ~2× GTCRN | — | Avoid — 32 ms look-ahead kills latency |
| DeepFilterNet2 | 1.78 M | 0.35 G | 2.81 | Fallback; more mature tooling |
| FullSubNet+ | 8.67 M | 30 G | 2.88 | Too heavy for edge |
| DEMUCS | 18.87 M | 4.32 G | 2.93 | Far too heavy |

## 8.2 Recommendation: GTCRN

GTCRN reaches PESQ 2.87 on VCTK-DEMAND and DNSMOS 3.44 on the DNS3 blind test with only 23.7K parameters and 39.6 MMACs per second.

The PS target is PESQ > 2.5. **GTCRN clears it with a model 75× smaller than DeepFilterNet.** That is not just adequate — it becomes an argument:

> At 39.6 MMACs/s this runs on a sub-$5 microcontroller. The problem statement suggests a Jetson AGX Orin; we do not need one. For a soldier-worn headset, SWaP-C is the binding constraint, and our footprint is two orders of magnitude below the reference platform.

Fallback to DeepFilterNet2 if GTCRN training proves unstable — the ecosystem is larger and there are more reference implementations.

**Do not invent a novel architecture.** Every team can do that badly. Your differentiation is in the data, the validation and the metrics.

## 8.3 Training configuration

- Input: complex STFT, 20 ms window, 10 ms hop, 16 kHz (32 kHz if bandwidth allows)
- Loss: SI-SNR + multi-resolution STFT magnitude + optional perceptual term
- SNR range: −10 to +20 dB, uniformly sampled
- Dynamic mixing, seeded, on the fly
- Curriculum: pretrain on civilian noise → fine-tune on the impulsive mix

## 8.4 Impulse-specific handling

Add an auxiliary **impulse detection head** — a cheap binary classifier over frames. Two uses:

1. Feeds a gate that prevents the denoiser over-suppressing the frames immediately after a blast (the main cause of poor IRT)
2. Gives a free demo visual: live impulse markers on the spectrogram

---

# 9. Edge deployment

## 9.1 Pipeline

```
PyTorch → ONNX export → INT8 quantisation (post-training + QAT)
   ├─► TensorRT      (Jetson Orin, if using the reference platform)
   └─► TFLite Micro / CMSIS-NN   (Cortex-M, the SWaP-C argument)
```

## 9.2 Latency budget (measure, do not estimate)

| Stage | Budget |
|---|---|
| Frame buffering (10 ms hop) | 10 ms |
| Model inference | < 2 ms |
| I/O and buffer copy | ~5 ms |
| **Total Lane B** | **~17–20 ms** |
| Lane A (FxLMS, separate loop) | < 1 ms |

Instrument this and put the measured number on a slide. Most teams quote a theoretical figure.

## 9.3 Hardware-matched training — the real co-design USP

Once the prototype headset exists:

1. Measure its **primary path** (reference mic → error mic) and **secondary path** (speaker → error mic) via log sweep and deconvolution
2. Feed those measured IRs into the mixing engine
3. Retrain

The model is now matched to your specific hardware. No competing team can replicate this without your physical device. This is what "hardware-software co-design" actually means, and it directly serves the PS prototype-demonstration deliverable.

---

# 10. Phase plan

| Phase | Work | Owner | Critical path |
|---|---|---|---|
| **P0** | Repo scaffold, download all corpora, baseline mixing engine, reproduce GTCRN on VCTK-DEMAND | You | ✅ Blocks everything |
| **P1** | **IRT + WLPS metrics implemented and validated** | You | ✅ Cheapest USP, do early |
| **P2** | Path measurement tool (sweep → deconvolution → IR) | You | ✅ Friend needs it |
| **P3** | **Range session** | Both | ✅ **One-shot, no retry** |
| **P4** | Friedlander generator + parameter fitting from range fit set | You | |
| **P5** | Device chain calibrated against clipped range data | You | |
| **P6** | Full dataset generation, train GTCRN, run 4-way ablation | You | |
| **P7** | ONNX → INT8 → target, measure real latency | You | |
| **P8** | FxLMS lane on hardware, secondary path estimation | Friend | Parallel |
| **P9** | Integration, live demo UI, dry runs | Both | |

**Do P1 before P3.** If the range trip slips, you still have a research contribution.

**Do P2 before the hardware is finished.** Your friend will need the measurement tool the day the first prototype exists.

---

# 11. Deliverables mapped to the problem statement

| PS requirement | Your deliverable | Evidence |
|---|---|---|
| Dataset generation | Config-driven mixing engine + blast synthesiser + measured range corpus | Repo + dataset card + validation report |
| Training pipeline | GTCRN training with dynamic mixing, seeded configs | Repo + reproducible config hashes |
| Inference engine | Real-time streaming inference with impulse detection head | Repo + measured latency |
| Edge deployment | ONNX → INT8 → target, benchmarked | Latency and power table |
| Prototype demo | Live headset, hardware-matched model, ANC on/off toggle | Working device |
| SNR > 15 dB, STOI > 0.85, PESQ > 2.5 | Evaluation report on held-out real data | Metrics table + ablation |

**Extra deliverables (not requested — that is the point):**
- Physics validation report with published error bounds
- Energy-scaling validation chart
- IRT / WLPS metric definitions and results
- Measured acoustic path database for the prototype
- Dataset card documenting provenance, splits and limitations

---

# 12. USPs — ranked by defensibility

1. **Physics-validated synthetic data with published error bounds.** Not "we downloaded gunshots" — a measured, calibrated, quantified pipeline.
2. **Energy-scaling validation across ~45 dB.** Turns a legal access constraint into a rigorous methodology.
3. **IRT and WLPS metrics.** Demonstrates that standard metrics under-report impulsive damage. A real contribution, ~50 lines of code.
4. **Hardware-matched training via measured path IRs.** Genuine co-design. Physically impossible to copy.
5. **Device-chain modelling.** Clipping, AGC and vocoder simulation. Your model survives a clipped live demo when others fail.
6. **Correct two-lane architecture.** Most teams will claim a neural net does their active cancellation. Being right here is free.
7. **23.7K parameters.** Runs on a microcontroller, not a Jetson. A direct SWaP-C argument for a soldier-worn device.

Note that USPs 1, 2, 4 and 5 all come from **measurement**, not cleverness. That is why they cannot be copied by a team with a chatbot and a weekend.

---

# 13. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Range access denied | High | Balloons, firecrackers and whip crack need no range. Starter pistol from the sports department. |
| Starter pistol unavailable | Medium | Firecracker size sweep still gives the energy-scaling axis |
| Range recordings unusable (wind, clipping, no calibration) | **Critical** | Tier 0 discipline; listen back after the first 3 events; two recorders always |
| Hardware not ready in time | High | iks\|PANDAR paths let Lane B proceed with zero hardware |
| GTCRN training unstable | Medium | DeepFilterNet2 fallback, larger ecosystem |
| Latency target missed | Medium | Reduce hop size, quantise harder, drop to 16 kHz |
| Synthetic fails to match real | Low | Report the mismatch as a finding. Honest error bounds beat claimed perfection. |

---

# 14. Repository structure

```
zeit-anc/
├── data/
│   ├── raw/              # downloaded corpora (gitignored)
│   ├── measured/         # range recordings + metadata CSV
│   ├── paths/            # measured IRs (headset + range)
│   └── manifests/        # JSON manifests only — no audio in git
├── blastgen/             # Friedlander synthesiser + param fitting
├── mixer/                # config-driven dataset mixing engine
├── pathtools/            # sweep generation, deconvolution, IR extraction
├── device/               # clipping, AGC, vocoder simulation
├── models/               # GTCRN + impulse detection head
├── eval/
│   ├── standard.py       # PESQ, STOI, SI-SNR
│   └── impulse.py        # IRT, WLPS
├── deploy/               # ONNX export, INT8 quantisation, benchmarks
├── firmware/             # FxLMS lane (friend)
├── configs/              # every experiment is a config file
└── docs/
    ├── dataset_card.md
    ├── validation_report.md
    └── latency_report.md
```

Rule: **no audio in git.** Manifests and configs only. Every experiment reproducible from a config hash plus a corpus download script.

---

# 15. Division of work

**You (software):**
- Mixing engine, blast synthesiser, device chain
- Path measurement tooling (deliver to friend early)
- Model training, evaluation, ablations
- IRT / WLPS metrics
- ONNX export, quantisation, latency benchmarking
- Demo UI

**Friend (hardware):**
- Ear cup, mic placement, speaker selection
- Reference + error + boom microphone integration
- ADC/DAC, amplifier, power
- FxLMS implementation on DSP/MCU
- Physical path IR measurement using your tool

**Shared:**
- Range session
- Integration and demo rehearsal

---

# 16. One-line summary for the pitch

> We built a physics-validated synthetic dataset generator for impulsive defence noise, measured its accuracy against real impulsive sources across 45 dB of energy, showed that standard speech metrics under-report impulsive damage and proposed two that don't, and trained a 23.7K-parameter model that meets the PESQ and STOI targets on a microcontroller rather than a Jetson.
