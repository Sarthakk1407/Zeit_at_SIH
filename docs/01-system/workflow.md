# ZEIT — end-to-end workflow

SIH 2026, PS 26052 (DRDO) — AI/ML adaptive noise cancellation for defence.

Everything from microphone to deployed model, built only on what is actually in
the papers we have read. Where a claim comes from conversation rather than a
source, it is marked **[unverified]**.

Companion documents: [`DETAILS.md`](../02-data-collection/details.md) covers the real-data collection
system in full. [`WHAT_WE_MEASURE.md`](../02-data-collection/what-we-measure.md) covers every measured
quantity. This document covers everything else and ties them together.

---

## 0. What the problem statement actually demands

Five requirements, each one closing off a set of options:

| Requirement | What it rules out |
|---|---|
| **AI/ML-enabled** | A purely classical DSP solution. The core denoiser must be learned |
| **Adaptive** | Fixed settings. The system must change behaviour as the noise changes |
| **Stationary + non-stationary + impulsive** | Any method validated only on steady noise — which is most of the literature |
| **High speech intelligibility** | Aggressive suppression that eats the voice. Measured, not asserted |
| **Real-time on embedded hardware** | Large models. Latency and power become first-class constraints |

Targets: **SNR > 15 dB, STOI > 0.85, PESQ > 2.5**, real-time, low latency.

The third row is the one that matters. Gunshots and artillery are named in the
first paragraph of the PS, and — as §2 shows — almost nothing in the published
literature is tested on them.

---

## 1. The evidence base

Thirteen sources, grouped by what they contribute.

### 1.1 Foundations

| Source | Year | What it gives us |
|---|---|---|
| **Widrow — adaptive noise cancelling** | 1975 | The two-microphone architecture: a *primary* input (desired signal + noise) and a *reference* input (noise correlated with the primary). The reference is adaptively filtered and subtracted. LMS adjusts filter weights sample by sample with no prior knowledge of the noise |
| **NOISEX-92 (Varga & Steeneken)** | 1993 | A benchmark and a controlled SNR framework, not an architecture. Its noise set — engine, factory, babble, speech-shaped noise — is the set nearly every later paper inherits, and **none of it is impulsive** |

Widrow's result that matters for us: **if the reference mic contains zero
components of the soldier's own voice, the system is mathematically incapable
of cancelling that voice.** The filter minimises total output power, which
forces it to target only the noise. That is a placement constraint, not a
software one — see §3.

### 1.2 Learned speech enhancement

| Source | Year | Core idea |
|---|---|---|
| **Wang & Chen — supervised separation** | 2018 | Enhancement as supervised learning on noisy/clean pairs. Time-frequency masking; IBM and IRM as targets. Training data quality and diversity decide generalisation |
| **DCCRN** | 2020 | Complex-domain processing — magnitude *and* phase. Complex convolutions plus a recurrent stage for temporal change |
| **FullSubNet** | 2021 | Full-band branch for global spectral structure, sub-band branch for local frequency behaviour. Designed for real-time single-channel use |
| **DeepFilterNet2** | 2022 | Two stages: 32 ERB bands predicting real-valued gains (coarse), then complex "deep filtering" coefficients below 5 kHz rebuilding harmonic detail. Real-time on a Raspberry Pi 4 |
| **GTCRN (Rong et al., ICASSP)** | 2024 | Ultra-low-compute enhancement: ERB filter bank, grouped convolution, grouped RNN, subband feature extraction (SFE), temporal recurrent attention (TRA) |
| **H-GTCRN** | — | Hybrid dual-mic: Aux-IVA does a cheap blind first-pass separation, a modified GTCRN refines it — conditioned on **both** the raw noisy input and IVA's output |
| **IS³** | 2025 | Separates *impulsive* from *stationary* components in general acoustic scenes. Two-stage: ERB gain filtering, then complex deep filtering. Its data-generation pipeline is a major part of the contribution |

**On GTCRN's size — state both numbers.** The ICASSP paper reports **23.7K
parameters and 39.6 MMAC/s**. The official implementation reports **48.2K
parameters and 33.0 MMAC/s** because of implementation and accounting changes.
Quote the pair, not the flattering one. A judge who knows the repo will check.

H-GTCRN reports **~24K parameters, ~43 M operations/s**, and beats plain GTCRN
and larger dual-channel baselines at **−12.5 dB to −2.5 dB SNR** — the regime
gunfire actually produces.

### 1.3 Impulsive noise specifically

| Source | Year | What it gives us |
|---|---|---|
| **Ruhland, Bitzer, Brandt & Goetze — BMRI** | 2015 | Two-stage classical pipeline. Stage 1: frequency-dependent adaptive threshold (fast release / slow attack) splits each block into "target" and "residual". Stage 2: an AR model predicts each residual sample from its neighbours; the worst γ% are flagged impulsive and interpolated back in, then a spectral-correction pass removes rumble artifacts |
| **Yuan, Li & Kuruoğlu — α-stable training noise** | 2023 | Replace Gaussian augmentation with α-stable noise. α controls tail heaviness (α=2 is Gaussian, α=1 is Cauchy, smaller α means more violent spikes). Justified by the Generalized CLT. Beats Gaussian augmentation, most clearly when test data is impulsive; they recommend α ≈ 1 |

BMRI's design constants matter for the edge target: **2048-sample blocks, AR
order 16 or 32, single interpolation pass, no neural component.** That is a
real-time-capable classical path we can put *beside* the neural one.

BMRI's own weakness, stated by its authors: steady Gaussian noise. That is
exactly where the neural path is strong. The two are complementary.

### 1.4 The two closest prior systems — and why neither finishes the job

| Source | Year | What it is |
|---|---|---|
| **Deep ANC (Zhang & Wang)** | 2021 | Reframes active noise control as supervised learning. A CRN predicts the anti-noise via complex spectral mapping. Delay-compensated training predicts M frames ahead to claw back STFT latency |
| **Dual-mic DC-CRN (Tan, Zhang & Wang)** | 2021 | Densely-connected convolutional recurrent network, dual-channel complex spectral mapping, structured pruning with sparse group lasso: **290.44K → 103.07K parameters** with little quality loss |

These two are the nearest published work to what the PS describes. §2 is about
where they stop.

---

## 2. The gaps we build on

From the gap analysis, ordered by how much they matter to us. Each one is a
place a published method stops short of what the PS demands.

### 2.1 No impulsive noise anywhere in Deep ANC

Deep ANC's test noises are engine, factory, babble and SSN from NOISEX-92 —
every result table. All four are stationary or close to it. Training used a
sound-effects library that probably contained transients, but nothing was ever
*tested* on them.

**The foundational deep-ANC paper does not address the noise class our sponsor
names first.**

→ *What we do:* run the test the authors never ran. Their architecture (or
GTCRN as a stand-in) trained on their kind of data, evaluated on our impulsive
set. Report the collapse honestly.

### 2.2 Delay compensation assumes the noise is predictable

Deep ANC buys back latency by predicting the anti-noise M frames ahead. With
20 ms frames and a 10 ms hop, each frame of prediction buys 10 ms.

Its cost, on engine noise (their Table 1):

| Model | NMSE (dB) |
|---|---|
| CRN-n, no prediction | −11.07 |
| CRN-n(−1), 1 frame ahead | −9.60 |
| CRN-n(−2), 2 frames ahead | −7.93 |

Roughly **1.5–1.7 dB of cancellation lost per 10 ms bought back** — on
*periodic* noise.

**Prediction only works if the future resembles the past.** A gunshot is by
definition unpredictable: there is no information in the milliseconds before it
that says it is coming. So the mechanism that makes deep ANC real-time-viable
should degrade far worse on impulsive noise than 1.5 dB per frame. Nobody has
measured this.

→ *What we do:* replicate that table with impulsive noise substituted in. Plot
NMSE against prediction horizon for stationary and impulsive on the same axes.
If the impulsive curve falls off a cliff while the stationary one declines
gently, that single chart carries the whole project.

→ *And it dictates the architecture:* **if you cannot predict a gunshot, you
must detect and react instead.** That argues for a hybrid — a neural path for
predictable noise, a fast transient path that gates or interpolates across the
burst. See §4.

### 2.3 RMS normalisation is formally invalid for impulsive noise

The dual-mic paper rescales every mixture so the waveform RMS equals 1. The
authors are honest that this is not causal and that deployment would need
causal AGC.

But there is a deeper problem. RMS is a **second-moment (variance-based)**
statistic. The α-stable paper states directly that for α < 2 the **variance is
infinite**. You cannot normalise heavy-tailed audio by RMS in any principled
way.

Practically: a gunshot 40 dB above the speech dominates the RMS, so normalising
fills the range with the gunshot and squashes speech toward the numeric noise
floor — and the scale factor changes depending on whether a gunshot happened to
land inside the window.

**The preprocessing breaks before the model runs.**

→ *What we do*, in order of ambition:
1. **Percentile-based scaling** — normalise on the 90th percentile of magnitude, so one spike cannot set the scale. Cheap, works, do this first.
2. **Fractional lower-order moments** — Shao & Nikias (1993), cited inside the α-stable paper. Moments of order below the tail index stay finite when variance does not.
3. **Causal AGC with a fast-attack limiter** — solves the deployment problem and the impulsive problem together.

This is the highest return-on-effort item in the entire stack: half a day's
work, a real bug in the closest prior system, explainable in thirty seconds.

### 2.4 Microphone-side clipping is modelled by nobody

Deep ANC carefully models *loudspeaker* nonlinearity — a scaled error function
with four nonlinearity levels, trained and tested. Good work, and all of it on
the **output** side.

Nothing models what happens when the **input** overloads.

At close range a gunshot exceeds 140 dB SPL; ordinary capsules saturate
somewhere above 110–120 dB. **The waveform arrives at the ADC already
flat-topped, with information physically destroyed before any algorithm sees
it.** No masking recovers it.

→ *What we do:* extend their nonlinearity framework to the input side — same
spirit, opposite end of the chain. Train the model to reconstruct through it,
and demonstrate with deliberately clipped recordings we made ourselves. Our
own range data gives us exactly this material, measured, with `validate.py`
recording precisely which events clipped and by how much.

### 2.5 The α-stable clipping constraint, inverted

The α-stable paper reports that at **α below 0.5**, roughly a third of image
pixel values ended up clipped, which they judged to compromise reliability — so
they set **0.5 as the lower bound on α**.

Read that from our side. For them clipping was an artifact of squeezing
unbounded noise into a bounded pixel range: a nuisance to design around. **For
us, clipping is the physics.** A microphone has a maximum SPL, a gunshot
exceeds it, and the signal clips at the sensor every single time.

They also note that truncated α-stable noise still beat truncated Gaussian —
the effect survives clipping, it just complicated their analysis.

→ *What we do:* deliberately generate α-stable noise **below their α = 0.5
floor**, apply it, and let it clip — because that is what a real capsule does.
Train the model to reconstruct speech through the clipped transient. We use the
regime they explicitly excluded, for the reason they excluded it.

### 2.6 α-stable augmentation has never touched audio

The authors state it themselves in their conclusion: noise substantially
affects audio, video and text, and extension to those is future work. Their
four datasets are two image sets and two time-series sets. **Not one audio
experiment.** And everything is classification; enhancement is regression, and
they list regression as unexplored.

→ *What we do:* be first — but **do not overclaim**. Frame it as a hypothesis
with a Gaussian-augmented baseline alongside. If it helps, we extended a
published method to a new task class. If it does not, we have an honest
negative result with an explanation. Assuming it works and quietly not checking
is the failure mode.

### 2.7 α-stable training produces sparser models — but nobody pruned them

The α-stable paper reports sparsity as a side effect: on MNIST-C, multiple
α-stable noise gives 6.16% and Cauchy 7.13% sparsity versus 3.02% for Gaussian;
on CIFAR10-C, 59.49% (Cauchy) against 51.62% (Gaussian). They connect it to
generalisation, cite the pruning literature — **and never prune anything**.

The dual-mic paper spends a whole section on structured pruning, 290K → 103K.

**The two papers do not cite each other.** The untested hypothesis sits in the
gap: a model trained with α-stable augmentation should prune further, or prune
to the same size with less quality loss.

→ *What we do:* train two identical models, one Gaussian-augmented, one
α-stable-augmented, prune both with the published iterative scheme, plot
quality against parameter count. **One experiment, two deliverables** — better
impulsive robustness *and* better edge compression, from a single training
change.

### 2.8 Smaller gaps worth knowing

| Gap | Where | What we do |
|---|---|---|
| Noise-trained ANC model *damages* speech (STOI 0.79→0.72, PESQ 1.95→1.71 at 5 dB) | Deep ANC Tables 2, Fig 9 | A lightweight VAD in front, or one model with a mixed objective that degrades gracefully |
| Deep ANC never deployed — authors list device implementation as future work | Conclusion | Quote it. It reframes us from "students reimplement a paper" to "we did the part the authors flagged unfinished" |
| One room, 3×4×2 m, T60 0.15–0.25 s, fixed geometry | Deep ANC §4.2 | Train across a wide spread of room responses including near-anechoic (open field) and hard-walled (vehicle interior), report each separately |
| Dual-mic paper trained and tested **only on babble** | Tan et al §IV-A | Run their architecture on a proper stationary / non-stationary / impulsive taxonomy, report the grid |
| Real-time claim measured on an i7 laptop (125.6 MMAC/s, 2.78 ms per 20 ms frame) | Tan et al §V-A | Measure on our actual board and publish it. Also **power — nobody reports watts.** Bring a USB power meter |
| Mic spacing fixed at 10 cm, never varied | Tan et al §IV-A | Re-simulate at our real headset geometry, and test robustness to spacing |
| Head shadow simulated as a flat −10..0 dB scaling | Tan et al §IV-A | Use published HRTF data instead. Real head shadow is strongly frequency-dependent |
| Explicit inter-channel features gave no benefit — but only for babble | Tan et al Table IV | Re-run the ablation with impulsive noise. An impulse is a single sharp wavefront with a well-defined arrival-time difference — exactly where inter-channel timing should carry information |
| They prune but never quantize | Tan et al §III-D | Add the quantization study. Note the interaction: prune-then-quantize ≠ quantize-then-prune, and enhancement is sensitive to reduced precision |
| α-stable noise is i.i.d.; real gunshots are structured | Yuan et al §4.1 | Generate **structured** α-stable bursts — heavy-tailed in when and how hard they arrive, but with a realistic attack/decay envelope |
| Choosing the dispersion parameter γ is open | Yuan et al §6 | In images there is no natural scale. **In audio there is: SNR.** Derive a mapping from target SNR to γ for a given α instead of a blind sweep |

### 2.9 The cross-paper findings

Three things visible only when all the papers are read together. None of these
papers cites the others in the relevant way.

**A. Deep ANC's latency trick and the α-stable noise model are in direct
conflict.** Deep ANC buys latency back by prediction; prediction needs
predictability. The α-stable premise is that impulsive noise is heavy-tailed —
dominated by rare, extreme, isolated events, which are by construction the
least predictable thing in a signal. **The mechanism that makes deep ANC
real-time-viable should fail exactly on the noise class the PS is about.**
Measured, this is the intellectual spine of the project.

**B. The dual-mic preprocessing is mathematically undefined under the α-stable
noise model.** RMS is a second moment; for α < 2 the variance is infinite. The
closest published dual-mic system has a preprocessing step that is not merely
fragile but formally invalid for our noise class. The fix is cited *inside* the
other paper.

**C. Both enhancement papers use squared-error losses, the wrong estimator
here.** Squared error is maximum-likelihood when the residual is Gaussian.
Under heavy tails it is dominated by outliers — one impulsive sample drags the
gradient more than a second of speech. L1 is better, still not matched. A loss
built on fractional lower-order moments would be principled. **Stretch goal
only** — most ambitious, most likely to fail, must not block anything.

---

## 3. Hardware and microphones

### 3.1 The two-microphone architecture

Straight from Widrow, and the reason it is not optional:

| Mic | Placement | Picks up |
|---|---|---|
| **Primary (Mic 1)** | Close to the mouth, inside the respirator / headset mask | The desired vocal command, corrupted by gunshot and explosion noise |
| **Reference (Mic 2)** | Exterior of the helmet, facing outwards | **Only** the environment — firearm and vehicle noise |

**The critical constraint:** if Mic 2 is structurally or spatially isolated so
that it contains **zero components of the soldier's own voice**, the system is
*mathematically incapable* of cancelling the speech. The adaptive filter
minimises total output power, which forces it to target only the noise.

Get the isolation wrong and the system eats the voice it exists to protect.
This is a mechanical design requirement handed to the hardware side, not
something software can fix afterwards.

### 3.2 Microphone SPL is the binding constraint

| Source | Approx peak SPL |
|---|---|
| Muzzle blast, close range | 140–155 dB |
| Ordinary capsule saturation | 110–120 dB |

Once the capsule or its internal FET saturates, **no pad, gain change or
algorithm downstream recovers the waveform.** Only distance helps.

Consequences for the build:
- **Dynamic (moving-coil) mic** for close blast work — no active electronics to overload
- **Measurement mic** for sweeps, calibration and ambience
- Distance as the primary level control; each doubling gives −6 dB
- The staggered-gain array (§4 of `DETAILS.md`) so one channel always survives

### 3.3 Edge target

The PS names Jetson AGX Orin *or similar*. The literature says a far smaller
target is achievable:

| System | Parameters | Compute | Demonstrated on |
|---|---|---|---|
| GTCRN (paper / official impl) | 23.7K / 48.2K | 39.6 / 33.0 MMAC/s | — |
| H-GTCRN | ~24K | ~43 M ops/s | — |
| Dual-mic DC-CRN, pruned | 103.07K | 125.6 MMAC/s | i7 laptop, 2.78 ms per 20 ms frame |
| DeepFilterNet2 | small | — | **Raspberry Pi 4, real time** |

**[unverified]** — none of these numbers has been reproduced by us. They come
from the reading notes, and the notes themselves say to verify against the PDFs
before putting anything on a slide.

The argument to make: SWaP-C is the binding constraint on a soldier-worn
headset, and a GTCRN-class model at tens of thousands of parameters makes a
Jetson unnecessary. **But measure it on our board before claiming it**, and
report **watts** — which nobody in the literature does.

---

## 4. System architecture

What falls out of §2, rather than what looks impressive.

```
  Mic 1  primary, at mouth ──┐
                             ├─→  robust normalisation        (2.3)
  Mic 2  reference, helmet ──┘     percentile / FLOM, never RMS
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                    transient detector          neural core
                    fast, kurtosis-based        GTCRN-class, complex
                    classifies the frame        ERB + grouped conv/RNN
                              │                       │
                    ┌─────────┴─────────┐             │
                    │                   │             │
              IMPULSIVE path      STATIONARY path     │
              BMRI-style:         learned mask        │
              AR detect +         via the neural core │
              interpolate                             │
                    │                   │             │
                    └─────────┬─────────┘─────────────┘
                              │
                    speech-intelligibility guard      (5.4 of the BMRI notes)
                    spectral correction, removes
                    regained LF rumble
                              │
                    optional LMS residual stage       (Widrow)
                              │
                        enhanced speech
```

### Why this shape

**Two paths, because prediction fails on impulses (2.2).** The neural core
handles what is predictable. The transient path detects and reacts — it does
not try to predict. That is the direct consequence of cross-finding A, and it
is the architectural claim the project rests on.

**BMRI as the impulsive path**, because it is proven on exactly this noise
class, is genuinely lightweight (2048-sample blocks, AR order 16/32, single
pass, no neural component), and its acknowledged weakness — steady Gaussian
noise — is precisely where the neural core is strong.

**GTCRN-class as the neural core**, because it is the smallest architecture
with published enhancement results, and H-GTCRN shows the dual-mic hybrid form
works at the negative SNRs gunfire produces.

**Robust normalisation in front of everything**, because RMS is formally
invalid here (2.3) and a broken preprocessing step makes every downstream
result meaningless.

**The adaptive element the PS demands** is the transient classifier: it
estimates residual kurtosis, classifies the frame as stationary /
non-stationary / impulsive, and tunes the detection percentage γ and threshold
offset β. That is what makes it *adaptive* rather than a fixed pipeline.

**Operator-selectable mission modes** fall out for free, because γ has a known
relationship to noise reduction: a low-γ *listening* mode preserving ambient
situational cues, a high-γ *combat* mode aggressively protecting voice commands
during gunfire.

---

## 5. Dataset generation

### 5.1 The structure

```
real gunshots (~60 events, one range trip)
        │
        ├──→ measured reference signature      (16 metrics, see WHAT_WE_MEASURE.md)
        │           │
        │           ▼
        │    validate the synthetic generator ──── the dataset-quality claim
        │           │
        ▼           ▼
   range IR ──→ synthetic noise generator
                        │
                        ├── gunshot, structured α-stable bursts
                        └── rotor, vehicle, siren, wind  (public corpora)
                        │
                        ▼
        clean speech corpus ──+──  training mixtures ──→ DNN
```

**The real recordings are not the training set.** They are the reference. The
DNN trains on generated audio, which is effectively unlimited — the limit is
compute, not recordings.

### 5.2 Real data — already built

The complete real-data collection system is documented in
[`DETAILS.md`](../02-data-collection/details.md): 96 kHz / 24-bit, staggered-gain array, calibration
to absolute Pascals, range impulse response, nine automated quality checks with
a GO/NO-GO verdict at the range, per-recording folders, a frozen reference with
checksums of both the data *and* the measurement engine.

Sizing, from [`WHAT_WE_MEASURE.md`](../02-data-collection/what-we-measure.md) §8: **never below 10
shots per condition, 15 for the core.** At 3 shots the standard deviation — the
tolerance any synthetic set must land inside — is itself ±46% uncertain, which
makes both "it matches" and "it does not match" unfalsifiable.

### 5.3 Synthetic generation — the template is IS³

IS³ faced our exact problem: no large standard dataset existed for
impulsive–stationary separation, so they built one. Their pipeline is the
template:

| IS³ did | Our equivalent |
|---|---|
| Stationary sources: DCASE2018 Task 1, CochlScene, Arte, CAS2023, LITIS Rouen | Vehicle, rotor, HVAC, wind from public corpora + our range ambience |
| Impulsive sources: ESC-50, ReaLISED, VocalSound, FreesoundOneShotPercussive, Nonspeech7k | **Our own measured gunshots** — this is the part nobody else has |
| Synthetic impulsive: chirps, harmonic summations, AR-filtered noise with asymmetric Gaussian envelopes | Structured α-stable bursts with measured attack/decay envelopes (2.8) |
| Synthetic stationary: pink-noise variants with EQ, gain, reverberation augmentation | Same, plus our measured range IR |
| Onset detection / Gabor decomposition to remove impulsive events from backgrounds | `dsp.find_events` already does the detection half |
| SALT taxonomy to standardise labels | Our metadata schema |

### 5.4 Augmentation — where the novelty is

1. **α-stable noise instead of Gaussian**, α ≈ 1 (2.6). Multiple separate α values beat blending them into one mixture.
2. **Below the α = 0.5 floor, and let it clip** (2.5) — the regime they excluded, which is our physics.
3. **Input-side saturation model** (2.4) — a saturating function applied to the mic signal in the data pipeline, mirroring their loudspeaker SEF at the opposite end of the chain.
4. **Structured bursts, not i.i.d. spikes** (2.8) — heavy-tailed arrival and amplitude, realistic envelope.
5. **γ derived from target SNR** (2.8), not swept blindly.
6. **Wide room-response spread** (2.8) — near-anechoic through hard-walled, reported separately.
7. **HRTF-based head shadow** (2.8) instead of a flat scalar.

### 5.5 Clean speech — still undecided

The PS implies Hindi and English. Nothing has been chosen. **This directly
determines training-set size and is the largest open item in the dataset
plan.**

### 5.6 SNR range

The literature's normal range is 0 to +20 dB. H-GTCRN targets **−12.5 to
−2.5 dB**, and that is the regime gunfire actually produces. Train and report
across both, and state the split — the PS target of SNR > 15 dB improvement is
much easier to hit from a high-SNR start than from −10 dB.

---

## 6. Training

| Element | Choice | Source |
|---|---|---|
| Representation | Complex STFT — magnitude **and** phase | DCCRN |
| Frequency compression | ERB bands | GTCRN, DeepFilterNet2, IS³ |
| Structure | Full-band + sub-band branches | FullSubNet |
| Efficiency | Grouped convolution, grouped RNN, SFE, TRA | GTCRN |
| Output | Mask applied to the **noisy input**, not to a pre-separated estimate | H-GTCRN ablation |
| Dual-channel conditioning | Feed **both** the separated-speech and separated-noise channels | H-GTCRN ablation — largest single gain in their study |
| Loss | SI-SNR + L1 on real/imaginary/magnitude, multi-resolution spectrogram loss | DeepFilterNet2, Tan et al |
| Loss (stretch) | Fractional lower-order moments | Cross-finding C — stretch goal only |
| Augmentation | α-stable, α ≈ 1, multiple values | Yuan et al + our extensions |
| Normalisation | Percentile or FLOM, **never RMS** | Cross-finding B |

The H-GTCRN ablation findings are worth restating because they are cheap wins:
applying the mask to the original noisy input beats applying it to IVA's
output; the log-power feature beats the full complex feature; and feeding both
speech *and* noise channels gives the largest gain of the three.

---

## 7. Evaluation

### 7.1 Metrics

| Metric | What it measures | PS target |
|---|---|---|
| **SNR / SI-SNR** | Noise suppression | > 15 dB |
| **STOI** | Intelligibility — can the words be understood | > 0.85 |
| **PESQ** | Perceptual quality | > 2.5 |
| **NMSE** | Residual noise energy, for the ANC comparison | more negative is better |
| **DNSMOS SIG** | Speech quality alone | **4.1 target** |
| **DNSMOS BAK** | Background suppression alone | **4.2 target** |
| **Latency** | Per-frame processing time on the real board | real-time |
| **Power** | Watts on the real board | **nobody in the literature reports this** |

DNSMOS earns its place: it separates SIG from BAK, so **over-suppression
becomes visible**. If the filter lowers gunshot noise (high BAK) but drops SIG
below 3.5, DNSMOS flags that the device is degrading command clarity. That is
the exact failure mode the PS's intelligibility requirement is about, and a
single SNR number hides it completely.

### 7.2 The evaluation grid

The core experiment, from gaps 2.1 and 2.8:

|  | Stationary | Non-stationary | Impulsive |
|---|---|---|---|
| Deep ANC / CRN baseline | published | — | **the collapse** |
| Dual-mic DC-CRN | — | — | **unknown, never tested** |
| GTCRN / H-GTCRN | published | — | ? |
| BMRI (classical) | weak, admitted | — | strong, validated |
| **Ours** | ? | ? | ? |

Filling that grid honestly *is* the contribution. A published method failing on
a noise class it was never tested on is a real negative result, not a failed
demo.

### 7.3 The latency chart

NMSE against prediction horizon M, stationary and impulsive on the same axes
(2.2). If the impulsive curve falls off a cliff while the stationary one
declines gently, one chart carries the whole argument and motivates the
two-path architecture directly.

---

## 8. Edge deployment

1. **Structured pruning** — sparse group lasso, iterative prune-then-finetune. Whole groups, because hardware can actually skip them; scattered zeros still get multiplied. Reference: 290.44K → 103.07K with little quality loss.
2. **Quantization** — the study Tan et al never did. Report the interaction: prune-then-quantize is not the same as quantize-then-prune, and enhancement is sensitive to reduced precision because it manipulates fine spectral detail.
3. **α-stable vs Gaussian prune-ability** (2.7) — one experiment, two deliverables.
4. **ONNX / TensorRT conversion**, per the PS.
5. **Measure on the actual board**: MMAC/s, ms per frame, and **watts**.
6. **Hard design constraints from BMRI**: small block size, low AR order, single-pass interpolation — benchmark AR order and block length against latency and CPU budget.

---

## 9. What is genuinely ours

Ranked by return on effort — pick from the top, do not attempt all of them.

| # | Contribution | Effort | Why it is defensible |
|---|---|---|---|
| 1 | **Robust normalisation replacing RMS** | half a day | A real, explainable bug in the closest prior system, with a fix cited inside another paper |
| 2 | **The impulsive evaluation grid** | days | Published methods tested on the noise class they skipped. Interesting either way |
| 3 | **Latency vs prediction horizon, stationary vs impulsive** | days | One chart, unarguable, motivates the architecture |
| 4 | **α-stable augmentation for audio, including the clipped regime** | cheap | The authors named audio as future work themselves. We use the α range they excluded, for the reason they excluded it |
| 5 | **Input-side clipping model** | pairs with #4 | Nobody models mic saturation. We have our own measured clipped recordings |
| 6 | **α-stable training vs prune-ability** | one experiment | Serves both halves of the PS at once |
| 7 | **Measured, validated gunshot dataset** | the range trip | Nobody else at SIH will have measured, calibrated, holdout-split real gunshot data with a frozen reference |
| 8 | FLOM loss | stretch | Most novel, most likely to fail. Must not block anything |

Items 1–6 come from the gap analysis. Item 7 is already built and is the part
no chatbot and no weekend can reproduce.

---

## 10. Build order

| Phase | What | Depends on |
|---|---|---|
| **P0** | Real data collection at the range | — **built, waiting on hardware** |
| **P1** | Robust normalisation + the impulsive evaluation grid | public corpora only |
| **P2** | Latency vs prediction-horizon chart | P1 baseline |
| **P3** | Synthetic generator, validated against the real reference | P0 |
| **P4** | α-stable augmentation, clipped regime, structured bursts | P3 |
| **P5** | Train the two-path architecture | P4 |
| **P6** | Prune, quantize, deploy, measure on the board | P5 |
| **P7** | α-stable vs prune-ability comparison | P6 |

**P1 and P2 need no hardware and no range data.** They can start immediately,
and they produce the baseline-collapse result and the latency chart — the two
findings the whole story rests on.

---

## 11. What is unverified, and the two cautions

**Unverified in this document:**
- Every number in §1 and §3.3 comes from reading notes, not from our own reading of the source PDFs
- GTCRN's parameter count is reported two different ways by two sources; both are quoted
- No claim here has been reproduced experimentally by us

**From the gap analysis, restated because they matter:**

> **Verify before you cite.** Sections and tables are pointed to rather than
> reproduced. Open each one and confirm before it goes near a slide. If a
> number in the notes disagrees with the paper, the paper is right.

> **A gap in the literature is not automatically a good project.** Sometimes
> nobody did a thing because it does not work, or because it does not matter.
> Gaps 2.2, 2.3, 2.5 and 2.7 are defensible as genuinely valuable. The rest are
> worth checking before committing weeks.

**Open decisions:**
1. Clean speech corpus — undecided, and it sets the training-set size
2. Target board — unnamed
3. Mic models and exact headset geometry — with the hardware team
4. Whether Aux-IVA (H-GTCRN's first stage) is worth its cost on our geometry

---

## Sources

Source notes are in [`../our notes from research paper/`](../../our%20notes%20from%20research%20paper/):
`PS26052_paper_gap_analysis.docx` (Deep ANC, dual-mic DC-CRN, α-stable — the
gap analysis §2 is built on), `Combined_Research_Papers_GTCRN_IS3_NOISEX92.docx`,
`Speech_Enhancement_Literature_Review.docx` (H-GTCRN, DeepFilterNet2),
`1.docx` (Wang & Chen, FullSubNet, DCCRN),
`ANC_Hackathon_Problem_Solution.pdf` (Ruhland BMRI), and the two Notes
screenshots covering Widrow and the DNSMOS targets.

| # | Work | Year |
|---|---|---|
| 1 | Widrow et al. — Adaptive Noise Cancelling | 1975 |
| 2 | Varga & Steeneken — NOISEX-92, *Speech Communication* 12(3) 247–251 | 1993 |
| 3 | Shao & Nikias — fractional lower-order moments (cited via Yuan et al.) | 1993 |
| 4 | Ruhland, Bitzer, Brandt & Goetze — Binary Mask Residual Interpolation, *IEEE/ACM TASLP* 23(10) 1680–1691 | 2015 |
| 5 | Wang & Chen — Supervised Speech Separation | 2018 |
| 6 | DCCRN — complex-domain speech enhancement | 2020 |
| 7 | Zhang & Wang — A deep learning approach to active noise control, *Neural Networks* | 2021 |
| 8 | Tan, Zhang & Wang — Dual-microphone real-time speech enhancement, *IEEE/ACM TASLP* | 2021 |
| 9 | FullSubNet — full-band and sub-band fusion | 2021 |
| 10 | DeepFilterNet2 | 2022 |
| 11 | Yuan, Li & Kuruoğlu — Robustness Enhancement with Alpha-Stable Training Noise, arXiv | 2023 |
| 12 | Rong et al. — GTCRN, ICASSP | 2024 |
| 13 | H-GTCRN — hybrid dual-channel Aux-IVA + GTCRN | — |
| 14 | IS³ — Generic Impulsive–Stationary Sound Separation, arXiv:2509.02622, WASPAA | 2025 |
