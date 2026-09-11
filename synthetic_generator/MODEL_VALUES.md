# Every value the ML model needs

Sourced from `workflow.md` §6–7, `tech-stack.md` §2, `architecture.md`, and the
reference measured on 7 Sep 2026.

---

## 1. Audio front end

| Value | Setting | Source / note |
|---|---|---|
| Engine sample rate | 48 000 Hz | `tech-stack.md` §2 |
| Neural core rate | **16 000 Hz** | GTCRN / H-GTCRN as published |
| Frame length | 20 ms (engine) / **32 ms (GTCRN)** | ⚠️ these disagree — see §6 |
| Hop | 10 ms (engine) / 16 ms (GTCRN) | |
| Window | Hann, √-Hann analysis/synthesis | overlap-add, phase preserved |
| FFT size | 512 @ 16 kHz → 257 bins | GTCRN's published arithmetic |
| ERB bands | **64** from 192 high bins, **65** low bins unaltered → 129 features | GTCRN band merging |
| Domain | **Complex** STFT — magnitude *and* phase | DCCRN |
| Capture rate (ours) | 96 kHz spec / **48 kHz actual** | field constraint |

## 2. Model architecture

| Value | Setting | Source |
|---|---|---|
| Backbone | GTCRN-class | `workflow.md` §6 |
| Parameters | **23.7 K** | GTCRN published |
| Compute | **39.6 MMAC/s** | GTCRN published |
| Structure | Full-band + sub-band branches | FullSubNet |
| Efficiency blocks | Grouped conv, grouped RNN, SFE, TRA | GTCRN |
| Output | Mask applied to the **noisy input**, not to a pre-separated estimate | H-GTCRN ablation |
| Dual-channel input | Feed **both** separated-speech and separated-noise channels | H-GTCRN — largest single gain |
| Front separation | Aux-IVA | +0.20 MMAC/s per iteration |
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

## 6. ⚠️ The rate conflict that must be resolved before training

| Component | Rate | Frame / hop | STFT latency |
|---|---|---|---|
| Our recordings | 48 kHz | — | — |
| `tech-stack.md` engine | 48 kHz | 20 / 10 ms | 25.3 ms budget |
| GTCRN / H-GTCRN as published | **16 kHz** | **32 / 16 ms** | **~48 ms** |

GTCRN's 129-feature band map assumes 257 bins from a 512-point FFT at 16 kHz.
Change the frame size or rate and the published 23.7 K parameters and
39.6 MMAC/s **stop applying** and the model must be retrained from scratch.

**Decide and write it down:** retrain at 20/10 ms (costs the published numbers,
buys the budget) **or** adopt 32/16 ms (keeps the numbers, costs ~23 ms).
Claiming both silently will not survive questioning.

Also write down the rate chain: 48 kHz capture → 16 kHz core → mask upsampled
back. Name the anti-alias filters; their latency is part of the budget and is
currently uncounted.

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
| Target | Jetson AGX Orin (PS names it) or DSP / AI SoC |
| Export | PyTorch → **ONNX** (the only Python↔C++ boundary) |
| Runtime | ONNX Runtime / TensorRT |
| Quantisation | INT8 post-training, per-channel |
| Pruning | structured; α-stable training yields sparser models — nobody pruned them |
| Algorithmic latency | **25.3 ms** budget |
| Compute per hop | **10 ms** |
| I/O buffer | 128 samples |
| Threads | RT audio callback / high-prio processing / normal control |
| RT rules | no allocation, no locks, no exceptions, no logging in the callback |
| FFT | PFFFT (not FFTW — GPL) |

## 10. Two-lane split — restore this

Deep ANC is **active control**: anti-noise through a loudspeaker, NMSE at an
error mic. GTCRN outputs enhanced speech, not an anti-noise waveform. They are
not interchangeable.

| Lane | Path | Budget | Algorithm | Metric |
|---|---|---|---|---|
| **A — hearing protection** | reference mic → speaker → ear | **sub-millisecond** | FxLMS + secondary-path estimation | NMSE / in-ear attenuation |
| **B — radio uplink** | boom mic → denoiser → radio | 20–40 ms | GTCRN-class DNN | PESQ / STOI / SI-SNR |

A neural network cannot live in Lane A: anti-noise must be emitted before the
wave physically reaches the ear — microseconds of headroom, not milliseconds.
The current 25.3 ms budget is 40–80× too slow for true ANC.

`project-plan-v0.md` §1.1 had this right and it was dropped in the rewrite.

## 11. Missing from the chain — the vocoder

A tactical radio transmits **MELPe** (STANAG 4591) at 2400 / 1200 / 600 bps,
narrowband, with its own noise pre-processor and post-filter.

PESQ and STOI are currently measured in the wrong place — they score the
denoiser's output, but the listener hears the vocoder's output. Put an open
MELPe or Codec2 in the evaluation chain and **report every metric twice, before
and after**. If two methods swap rank across the vocoder, that table is more
original than anything else in the plan.
