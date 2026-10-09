# Every value the ML model needs

Follows the locked architecture in `docs/01-system/architecture.md` (§6 is the
neural network), the hardware in `HARDWARE.md`, and the reference measured on
7 Sep 2026. The code that uses these values is `training/`.

---

## 1. Audio front end

| Value | Setting | Source / note |
|---|---|---|
| Capture rate | 48 000 Hz, 768-sample blocks | UMC404HD (H14) |
| Model rate | **16 000 Hz** | GTCRN native; 3:1 stateful FIR resampling |
| Frame length | **32 ms** (512 samples) | Locked |
| Hop | **16 ms** (256 samples) | Locked |
| Window | √-Hann (periodic) analysis and synthesis | overlap-add, phase preserved |
| FFT size | 512 @ 16 kHz → 257 bins | GTCRN's published arithmetic |
| ERB bands | **64** from 192 high bins, **65** low bins unaltered → 129 features | GTCRN band merging |
| Domain | **Complex** STFT — magnitude *and* phase | DCCRN |
| Inputs (locked order) | 0 = Mic 1 boom · 1 = reference (Mic 2R, or 2L for left-handed) · 2 = Mic 4 throat | UMC in 1 / 2 / 3 |

## 2. Model architecture

| Value | Setting | Source |
|---|---|---|
| Backbone | GTCRN, re-implemented, 3 microphone inputs | `training/zeit/model.py` |
| Parameters | **25,109** (3 inputs) · 24,389 (2) · 23,669 (1) | MEASURED; paper reports 23.7 K for 1 input |
| Compute | ≈ 33–40 MMAC/s class (paper: 39.6; official code: 33.0) | Published, single-channel |
| Structure | Full-band + sub-band branches | FullSubNet |
| Efficiency blocks | Grouped conv, grouped RNN, SFE, TRA | GTCRN |
| Output | Mask applied to the **noisy input**, not to a pre-separated estimate | H-GTCRN ablation |
| Extra inputs | Reference mic (noise, little voice) and throat mic (voice, little noise) as additional channels | H-GTCRN idea; INVISIO body-conducted voice principle |
| Throat dropout | Input 2 zeroed for ≈ 30 % of training examples | One model works with or without the throat mic |
| Front separation | **None** — Aux-IVA removed (underdetermined with 2–3 mics) | Architecture §5.3 |
| Transient path | BMRI-style AR detect + interpolate | AR order 16–32 |
| Adaptive control | Kurtosis classifier → γ, β | ours |

## 3. Training

| Value | Setting |
|---|---|
| Loss | **SI-SNR** + L1 on real / imag / magnitude + multi-resolution spectrogram |
| Loss (stretch) | Fractional lower-order moments |
| Optimiser | Adam / AdamW |
| Learning rate | 1e-3 → cosine or plateau decay |
| Batch size | 16–32 × 4 s segments |
| Epochs | 100–200, early stop on validation SI-SNR |
| Normalisation | **Percentile (90th) or FLOM — never RMS** |
| Gradient clip | 3.0–5.0 |
| Segment length | 4 s |

### Why never RMS

RMS is a second moment. For α-stable noise with α < 2 the variance is
**infinite**, so the statistic does not converge. This is a real defect in the
closest prior system and it is the highest return-on-effort item in the project.

## 4. SNR range

| Range | Why |
|---|---|
| **−12.5 to −2.5 dB** | H-GTCRN's regime — what gunfire actually produces |
| 0 to +20 dB | the literature's normal range |
| **Report as curves vs input SNR, not single numbers** | see §7 |

## 5. Augmentation — where the novelty is

| # | Technique | Value |
|---|---|---|
| 1 | α-stable noise, **not** Gaussian | α ≈ 1, multiple separate values (never blended) |
| 2 | **Below the α = 0.5 floor, and let it clip** | the regime Yuan et al. excluded — our physics |
| 3 | Input-side saturation model | saturating fn on the mic signal |
| 4 | Structured bursts, not i.i.d. spikes | heavy-tailed arrival + amplitude |
| 5 | γ derived from target SNR | not swept blindly |
| 6 | RIR spread | near-anechoic → hard-walled, reported separately |
| 7 | HRTF head shadow | CIPIC / KEMAR, not a flat scalar |
| 8 | Reverberation, random gain, clipping | PS names these explicitly |

## 6. Rate chain — resolved

The earlier conflict (48 kHz / 20 ms engine vs GTCRN's 16 kHz / 32 ms) is
resolved in favour of **GTCRN's native settings**, so its band layout and
published size stay valid.

| Stage | Rate | Frame / hop | Delay |
|---|---|---|---|
| Capture (UMC404HD) | 48 kHz | 768-sample blocks | ≈ 16 ms buffer |
| Decimation 48 → 16 kHz | 96-tap FIR, cut-off 7.2 kHz, stateful | — | ≈ 1 ms |
| Model | 16 kHz | 32 / 16 ms | 32 ms window |
| Interpolation 16 → 48 kHz | same FIR | — | ≈ 1 ms |
| Output buffer | 48 kHz | 768 samples | ≈ 16 ms |
| **Mouth to radio** | | | **≈ 70–85 ms** (ESTIMATE; ITU-T G.114 limit 150 ms) |

## 7. Evaluation targets

| Metric | PS target | Best in our 15 papers | Reality check |
|---|---|---|---|
| SNR / SI-SNR | **> 15 dB** | 8.61 dB (Tan et al.) | nothing published reaches 15 |
| STOI | **> 0.85** | 0.82 @ −2.5 dB (H-GTCRN) | crossed only above ~0 dB |
| PESQ | **> 2.5** | 1.71 @ −2.5 dB (H-GTCRN) | crossed only at high SNR |
| DNSMOS SIG | 4.1 (from a Notes screenshot) | **3.00** (GTCRN blind test) | not reachable |
| DNSMOS BAK | 4.2 (same) | 3.90 (GTCRN) | close-ish |
| NMSE | more negative | −11.07 dB (Deep ANC) | ANC only, not enhancement |
| Latency | real-time | — | measure on the board |
| Power | — | **nobody reports it** | free differentiator |

**Report every metric as a curve against input SNR from −15 to +20 dB and state
where you cross.** Also settle whether "SNR > 15 dB" means output SNR or ΔSNR —
improvement from −10 dB is a completely different claim from absolute 15 dB.

Add SI-SDR alongside SDR: Le Roux et al. (already in `docs/research/`) show SDR
stays flat or *rises* as frequency bins are deleted, while SI-SDR falls
monotonically. Deleting bins is exactly what a mask-based denoiser does — that
is the over-suppression argument, with a citation.

## 8. Real reference — what synthetic must match

From `REFERENCE_REAL/analysis/stats_impulse.json`, n = 44, **uncalibrated (dBFS)**.

| Metric | mean | sd | median |
|---|---|---|---|
| a_duration_ms | 0.67 | 0.71 | **0.27** |
| b_duration_ms | 366.7 | 184.6 | 342.7 |
| rise_time_ms | 13.2 | 12.1 | 9.4 |
| crest_factor_db | 19.1 | 3.2 | 17.9 |
| kurtosis | 31.8 | 64.3 | **18.5** |
| centroid_hz | 3545 | 3244 | 1415 |
| rolloff95_hz | 8010 | 6803 | 4471 |
| peak_freq_hz | 1743 | 2137 | 592 |

Measure synthetic with **the same `analyze.py`**. A metric landing inside ±1 sd
counts as a match. Compare against the **holdout** split only — tuning on all
the real data and then comparing to it is circular.

## 9. Edge deployment

| Value | Setting |
|---|---|
| Target | **Jetson Orin Nano Super** (Lane B); ADAU1787 DSP (Lane A, no neural network) |
| Export | PyTorch → streaming **ONNX** (the only training ↔ device boundary) |
| Runtime | **TensorRT** FP16, then INT8; ONNX Runtime CUDA as fallback |
| Quantisation | INT8 post-training, per-channel |
| Pruning | structured; α-stable training yields sparser models — nobody pruned them |
| Algorithmic latency | **32 ms** (STFT window); ≈ 70–85 ms mouth to radio |
| Compute per hop | **16 ms** deadline, worst case |
| I/O buffer | 768 samples at 48 kHz |
| Threads | RT audio callback / high-prio processing / normal control |
| RT rules | no allocation, no locks, no exceptions, no logging in the callback |
| FFT | PFFFT (not FFTW — GPL) |

## 10. Two-lane split — now the architecture

Deep ANC is **active control**: anti-noise through a loudspeaker, NMSE at an
error mic. GTCRN outputs enhanced speech, not an anti-noise waveform. They are
not interchangeable.

| Lane | Path | Budget | Algorithm | Metric |
|---|---|---|---|---|
| **A — hearing protection** | reference mic → speaker → ear | **sub-millisecond** | FxLMS + secondary-path estimation | NMSE / in-ear attenuation |
| **B — radio voice** | boom + reference + throat mics → GTCRN → radio; radio receive → cleaning → ears | ≈ 70–85 ms | GTCRN (3 inputs) + classical blocks | PESQ / STOI / SI-SNR / IRT / WLPS |

Lane A runs on the ADAU1787 with no neural network: anti-noise must reach the
ear within ≈ 0.3–0.6 ms. Apple runs ML in its ear path on custom silicon, so it
is not physically impossible, but no DSP available to us offers that.

## 11. Missing from the chain — the vocoder

A tactical radio transmits **MELPe** (STANAG 4591) at 2400 / 1200 / 600 bps,
narrowband, with its own noise pre-processor and post-filter.

PESQ and STOI are currently measured in the wrong place — they score the
denoiser's output, but the listener hears the vocoder's output. Put an open
MELPe or Codec2 in the evaluation chain and **report every metric twice, before
and after**. If two methods swap rank across the vocoder, that table is more
original than anything else in the plan.
