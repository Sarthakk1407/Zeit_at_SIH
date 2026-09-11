# Checklist — tick as you go

Mark `[x]` when done and add the date. Anything marked ⚠️ is a claim risk: it
will be challenged by a technical judge.

**Last updated: 12 Sep 2026**

---

## Phase 0 — Foundations

### 0a. Data collection toolkit
- [x] 21 CLI tools built — *before 6 Sep 2026*
- [x] `selftest.py` prints ALL CHECKS PASSED — *6 Sep 2026*
- [x] All pinned deps installed (numpy 2.4.3, scipy 1.17.1, sounddevice 0.5.6, matplotlib 3.10.6)
- [x] Aggregate 2-channel input device working (`Zeit Range Array`) — *7 Sep 2026*
- [x] Add generated data folders to `.gitignore` — *8 Sep 2026* (`data for training/`, `REFERENCE_REAL/`, `VALIDATION_SET/`, `real shots/`, `data_collection/testdata/`)

### 0b. Baseline reproduction
- [ ] Deep ANC — reproduce published NMSE
- [ ] GTCRN — reproduce PESQ / STOI on VCTK-DEMAND
- [ ] H-GTCRN — reproduce the −12.5 / −7.5 / −2.5 dB table
- [ ] BMRI — reproduce SNR improvement on white Cauchy

### 0c. Public noise corpora ✅ DONE
- [x] Internet research — real sources verified with URLs and licences — *8 Sep 2026*
- [x] **MAD — Military Audio Dataset** — 7,466 files, via Kaggle — *10 Sep 2026*
- [x] **NOISEX-92** — 14 noises incl. leopard/m109 tanks, F-16, machine gun. Shipped as `.mat`, converted with `mat_to_wav.py` — *10 Sep 2026*
- [x] **Cadre Gunshot Forensics** — 2,241 files — *10 Sep 2026*
- [x] **Zenodo Gunshot/Gunfire** — 2,148 files — *11 Sep 2026*
- [x] **LibriSpeech** — 137,876 FLAC (train-clean-100 + 360, dev, test) — *11 Sep 2026*
- [x] **MUSAN** — 2,016 files — *11 Sep 2026*
- [x] **ESC-50** — 2,000 files — *10 Sep 2026*
- [x] **RIRs and Noises (OpenSLR28)** — 61,260 files — *10 Sep 2026*
- [x] **DEMAND** — 8 environments, 16-channel — *10 Sep 2026*
- [x] **UrbanSound8K** — 8,732 files — *12 Sep 2026*
- [ ] **FSD50K** ← the one still worth doing: 51k clips, gunshot/explosion/siren, **CC BY / CC0 (commercial-safe)**
- [ ] DroneAudioSet (MIT) — only if the drone class matters
- [ ] TAU Urban — optional, DEMAND already covers metro/bus/traffic and is 16-channel
- [ ] DREGON — optional
- [x] Licence tracked per corpus in `DATA_SOURCES.md`

**On disk: 11 datasets, ~229,000 audio files, ~100 GB.**
**Real gunshot recordings held: 6,147** (Zenodo 2,148 + Cadre 2,241 + MAD gunshot class 1,714 + our own 44).

### 0d. Clean speech 🟡 bulk downloaded, Hindi still open
- [x] Candidates researched with sizes, licences and URLs — *8 Sep 2026* (`DATASET_SPEC.md` §0.6)
- [ ] **DECIDE the corpus** ← blocks Phase 4 entirely
- [ ] ⭐ **SPRING-INX** — ~2,000 h, 10 Indian languages incl. Hindi, IIT Madras, **MeitY / Govt of India funded**
- [ ] **IndicVoices-R** — 1,704 h, 10,496 speakers, 22 languages
- [x] **LibriSpeech** — 137,876 FLAC on disk
- [ ] VCTK
- [ ] EARS
- [ ] Common Voice Hindi / IndicTTS / SPRING-INX
- [x] ✅ **Lombard GRID — DOWNLOADED**, 5,390 files (audio + alignment + metadata), *10 Sep 2026*. 54 talkers x (50 Lombard + 50 plain), paired.
- [ ] ⚠️ "Lombard" still appears **zero times** in `docs/01-system/` — the data is here, the docs have not caught up
- [ ] Use the alignment files: they carry word-level timings, so **WLPS needs no ASR on this corpus**

---

## Phase 1 — Real reference ✅

- [x] Range trip — *7 Sep 2026*
- [x] 15 takes recorded, 2 ch, 48 kHz / 24-bit
- [x] Per-shot folders in `DATA/` (raw, events, analysis, quicklook, validate)
- [x] 213 events sliced
- [x] 44 true impulsive events isolated
- [x] `analyze.py` run — per-event metrics as JSON + CSV
- [x] Reference statistics written (`stats_impulse.json`)
- [x] HTML reports generated
- [x] `VALIDATION_SET/` — 8 clean-channel takes
- [ ] ⚠️ **Calibration tone — NOT DONE.** All levels are dBFS, not dB SPL. No peak-overpressure or Friedlander claim is possible
- [ ] ⚠️ Range IR (balloon / sweep) — not captured
- [ ] ⚠️ Noise floor take — not captured
- [ ] ⚠️ Geometry + weather log — not recorded
- [ ] Second trip with a real firearm, calibrated, with a 2-in interface

**State honestly in the report:** air gun with target impact, not muzzle blast;
uncalibrated; channel 2 clipped and gated so the two-mic delay measurement did
not survive.

---

## Phase 2 — Baseline collapse

- [x] **2.1 Robust normalisation — percentile / FLOM vs RMS** — *9 Sep 2026*
      `synthetic_generator/experiments/p1_normalisation.py` + `.json` + `.png`
      Synthetic: at alpha=1.5 RMS spread stays 0.64→0.56 over a 1000x longer window (not converging);
      P90 falls 0.062→0.0010 and FLOM p=0.2 falls 0.030→0.0005. At alpha=0.5 RMS gets *worse* (2.11→3.29).
      At alpha=2 all four agree — the control that proves the method.
      Real 44 events, within-event: RMS drifts 18.0x median, FLOM p=0.2 drifts 5.7x — 3x less.
      Also reproduces the p < alpha rule: FLOM p=0.5 fails at alpha=0.5.
- [ ] 2.2 Impulsive evaluation grid
- [ ] 2.3 NMSE vs prediction horizon M — stationary and impulsive on one chart

---

## Phase 3 — Synthetic generator

- [ ] 3.1 Blast model + range-IR convolution + distance/propagation
- [ ] 3.2 Measure with **the same `analyze.py`**
- [ ] 3.3 Compare against the real **holdout only**
- [ ] Every metric inside ±1 sd of `stats_impulse.json`
- [ ] `session.py verify` confirms the engine has not changed

---

## Phase 4 — Training data 🔴

- [ ] 4.1 SNR mixing including **−12.5 to −2.5 dB**
- [ ] 4.2 α-stable, α ≈ 1, multiple separate values
- [ ] 4.3 Below α = 0.5, let it clip
- [ ] 4.4 Input-side saturation model
- [ ] 4.5 Structured bursts, not i.i.d. spikes
- [ ] 4.6 Wide RIR spread
- [ ] 4.7 HRTF head shadow

---

## Phase 5 — Model

- [ ] ⚠️ **Resolve the rate conflict** — 20/10 ms @ 48 kHz vs 32/16 ms @ 16 kHz. Write the decision down
- [ ] Write down the rate chain (48 k → 16 k → mask upsample) incl. anti-alias filter latency
- [ ] 5.1 GTCRN-class core
- [ ] 5.2 BMRI transient path
- [ ] 5.3 Kurtosis classifier → γ, β
- [ ] 5.4 Intelligibility guard
- [ ] 5.5 LMS residual stage
- [ ] 5.6 Train + evaluate on the Phase 2 grid
- [ ] Normalisation is percentile / FLOM — **never RMS**
- [ ] Mask applied to the **noisy input**, not IVA's output
- [ ] Both separated speech **and** noise channels fed to the network

---

## Phase 6 — Edge

- [ ] ONNX export
- [ ] INT8 quantisation
- [ ] Structured pruning
- [ ] Latency measured **on the board**
- [ ] **Power measured in watts** ← nobody in the literature reports this
- [ ] Numerical parity test: Python vs C++ stage by stage

---

## Phase 7 — Extra experiment

- [x] **IRT — Impulse Recovery Time** — `synthetic_generator/metrics/irt.py`, run on the 44 real events — *8 Sep 2026*
- [x] **WLPS — Words Lost Per Shot** — `synthetic_generator/metrics/wlps.py` — *8 Sep 2026*
- [ ] Run WLPS end-to-end. **Shortcut:** Lombard GRID's alignment files already carry word timings, so no ASR is needed on that corpus. For other corpora use one ASR (Whisper timestamps / Vosk / wav2vec2+CTC) and the SAME model for every system compared

---

## Claim risks — fix before any submission ⚠️

- [ ] Report PESQ / STOI / SNR as **curves vs input SNR**, state where you cross
- [ ] Settle whether "SNR > 15 dB" is output SNR or ΔSNR; report both
- [ ] Re-anchor DNSMOS targets — SIG 4.1 / BAK 4.2 came from a Notes screenshot; GTCRN's own blind test is SIG 3.00
- [x] Restore the **two-lane split** — done in `handbook/` (Lane A ≤1 ms, Lane B 25.3 ms; present across 14 source files)
- [ ] Fix the block-[10] wiring — Mic 3 is an in-ear error sensor, it cannot feed the radio uplink
- [x] Rewrite the look-ahead claim — done in `handbook/`: crack 45.2 ms vs blast 87.5 ms = **42.3 ms** genuine look-ahead; Mic1↔Mic2 is 0.58 ms
- [ ] Narrow BMRI's claimed job — validated on white Cauchy for film restoration, and it degrades transients
- [ ] Add the **MELPe / Codec2 vocoder** to the evaluation chain; report metrics before *and* after
- [ ] Cite Le Roux (SI-SDR) and Reddy (DNSMOS) — both already in `docs/research/`, both uncited
- [ ] Obtain the Shao & Nikias (1993) paper before FLOM goes into C++
- [ ] Add TRL statement — "we are at TRL 4; TRL 5 needs environmental qualification + field trial"
- [ ] Reference MIL-STD-1474 (140 dBP limit) and ANSI/ASA S3.2 (DRT/MRT intelligibility)


---

## Findings from work done 8 Sep 2026

### IRT measured on the 44 real impulsive events

34 of 44 had a clean pre-impulse window. Uncalibrated, so these are ratios
against each file's own baseline — which is exactly what IRT is designed for.

| | ms |
|---|---|
| IRT mean | 330.6 |
| IRT median | 107.0 |
| IRT p90 | 1022.5 |
| IRT max | 1265.5 |

Per band:

| Band | IRT |
|---|---|
| 125–250 Hz | 223.4 ms |
| 250–500 Hz | 288.6 ms |
| 500–1000 Hz | 404.6 ms |
| **1000–2000 Hz** | **464.4 ms** ← slowest |
| 2000–4000 Hz | 370.4 ms |
| 4000–8000 Hz | 232.0 ms |

**The band that recovers slowest is 1–2 kHz — the band that carries speech
intelligibility.** That is the argument for IRT in one line: a metric averaged
over a ten-second utterance cannot see a 464 ms hole in the most important band,
and PESQ and STOI are exactly such metrics.

Use this as the baseline. A system that lowers the 1–2 kHz IRT without raising
the others has genuinely recovered speech.

### Hardware — see `HARDWARE.md`

The bench already specifies a **Behringer UMC202HD**, a 2-input interface doing
24-bit up to 192 kHz. The 7 Sep trip failed on the two-mic half only because the
J13 wireless receiver is a 1-channel USB device. Using the UMC202HD on the next
trip fixes the channel count, the 96 kHz requirement, per-channel gain for the
staggered array, and the wireless AGC problem, all at once.
