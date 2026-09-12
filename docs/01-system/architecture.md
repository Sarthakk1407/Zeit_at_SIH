# Software architecture — the ZEIT engine

The product: a **headset that protects the wearer's hearing and keeps the
wearer's voice intelligible on the radio**, running in real time on a small
board.

There is no frontend and no backend here. There are **two engines** running side
by side on the same three microphones, with different physics, different budgets
and different metrics. Confusing them is the most common mistake on this problem
statement, so this document is organised around the split.

This document covers the deployed system only. The range-recording toolkit is a
separate thing and is not part of the product — see
[`../02-data-collection/details.md`](../02-data-collection/details.md).

Every algorithm is named, then explained in plain language.

---

## 1. What the device does

A soldier speaks into a headset while a gun fires nearby. Two things must happen
at once:

- **The wearer must not be deafened.** — Lane A
- **The person at the other end of the radio must hear the voice, not the
  gunshot.** — Lane B

Three physical facts make both hard:

1. **The gunshot is far louder than the voice** — 140–155 dB SPL against
   80–90 dB. A ratio of ten thousand or more in pressure
2. **It arrives with no warning** — nothing in the milliseconds before a gunshot
   says one is coming, so nothing can predict it
3. **It must run on a battery-powered board** — no cloud, no laptop

Everything in this architecture exists to solve one of those three.

---

## 2. Two lanes, not one system

```
                            +--------------------------------------+
   air ---> Mic 2 --------->|  LANE A - hearing protection         |
            (reference)     |  FxLMS on a dedicated loop           |---> driver
                       +--->|  budget < 1 ms                       |     (in the
             Mic 3 ----+    +--------------------------------------+      earcup)
            (in-ear)             error signal                                |
                                                                             v
                                                                    the wearer's ear

            Mic 1 --+
            (boom)  |       +--------------------------------------+
                    +------>|  LANE B - speech enhancement         |---> vocoder
            Mic 2 --+       |  11 blocks, GTCRN neural core        |     ---> radio
            (reference)     |  budget 25.3 ms algorithmic          |
                            +--------------------------------------+
```

| | **Lane A** | **Lane B** |
|---|---|---|
| **Goal** | The wearer hears less noise | The *transmitted* voice stays intelligible |
| **Path** | Mic 2 → filter → earcup driver → ear | Mic 1 + Mic 2 → 11 blocks → radio |
| **Error signal** | Mic 3, inside the cup | none — Mic 2 is a reference, not an error |
| **Method** | Emit an inverted copy so the two cancel in air — destructive interference | Estimate which parts are voice and keep only those — masking |
| **Budget** | **under 1 ms** | **25.3 ms algorithmic**, 10 ms compute per hop |
| **Algorithm** | FxLMS, classical. No neural network fits | GTCRN neural core plus a classical transient path |
| **Metric** | NMSE, or measured in-ear attenuation | PESQ, STOI, SI-SNR, DNSMOS |
| **Strong on** | Low-frequency continuous noise — engine, rotor, rumble | Broadband, non-stationary and impulsive content |
| **Owner** | Hardware / DSP | Software / ML |

**Why the split is not stylistic.** Sound crosses from the outer earcup shell to
the eardrum in roughly 0.3–0.6 ms. A feedforward canceller has to get its
anti-noise there first. Lane B's budget is 25.3 ms — forty to eighty times too
slow. Fuse the two lanes into one chain and the result cannot do active
cancellation at all, no matter how good the model is.

**The consequence for the pitch.** Everything the problem statement measures —
SNR, STOI, PESQ — is Lane B. Everything the phrase "active noise cancellation"
strictly means is Lane A. The PS asks for both, so the system must contain both,
and every number quoted must say which lane it belongs to.

---

## 3. The headset — 3 microphones

![Full architecture](../diagrams/4_architecture_full.png)

| Mic | Where | What it hears | Job | Lane |
|---|---|---|---|---|
| **Mic 1 — voice** | Boom arm, 2–5 cm from the mouth | Voice loud, gunshot quieter | The signal we want to keep | B |
| **Mic 2 — reference** | Outer surface of the earcup, opposite the boom | Environment only. Gunshot at full level, almost no voice | The noise reference | **A and B** |
| **Mic 3 — error** | Inside the earcup, beside the ear | What the ear actually hears after the cup blocks some sound | Tells Lane A how much is still leaking | **A only** |

### Why three and not two

With **two** microphones you can separate **two** things. With **three** you can
separate **three** — and the problem statement names exactly three noise classes:
**stationary** (engine hum), **non-stationary** (wind, vehicles) and **impulsive**
(gunshots).

Three microphones is also the smallest array that serves both lanes at once:
Lane A needs a reference *and* an error microphone, Lane B needs a primary *and*
a reference, and Mic 2 is shared between them.

> **Scope honesty.** Aux-IVA (block 2) is a *determined* method: N microphones
> separate at most N sources. A real scene has voice, blast, engine, wind and
> babble, which is underdetermined. Say "three separated streams, unordered" —
> not "voice / impulsive / background".

### The rule the hardware team must not break

**Mic 2 must not hear the voice.**

If it does, the system will cancel the voice — not by mistake, but because the
mathematics forces it to. An adaptive filter minimises total output power. If the
voice appears in the reference microphone, the mathematically optimal action is
to remove the voice. Widrow proved this in 1975.

So Mic 2 needs a physical barrier between it and the mouth: the earcup shell,
facing outward, with the boom on the opposite side of the head. This is a
mechanical decision. **Software cannot fix it afterwards.**

---

## 4. Lane A — hearing protection

A tight feedback loop that never touches the transmitted voice.

```
    Mic 2 ---> [ filtered-x by S_hat(z) ] ---> [ adaptive filter W(z) ] ---> driver
   reference                  ^                                               |
                              |                                               v
                              +--------------- Mic 3 <---- acoustic sum at the ear
                                              error
```

**FxLMS** — filtered-x Least Mean Squares. Ordinary LMS assumes the filter's
output reaches the error sensor instantly. Here it does not: the anti-noise has
to pass through a converter, an amplifier, a loudspeaker and a few centimetres of
air before Mic 3 measures the result. That path is the **secondary path** `S(z)`.
FxLMS filters the reference by an estimate `S_hat(z)` before the adaptation step,
which is what keeps the loop stable.

| Property | Value |
|---|---|
| Budget | **under 1 ms end to end** |
| Runs on | A DSP or microcontroller, not the application processor |
| Reference | Mic 2 |
| Error | Mic 3 |
| Output | Earcup driver |
| Metric | NMSE in dB, or measured in-ear attenuation |
| Genuinely good at | Low-frequency continuous noise |
| Cannot do | Broadband impulsive suppression — physics, not implementation |

**Why no neural network lives here.** The anti-noise must be emitted before the
acoustic wave physically arrives at the eardrum. That is microseconds of
headroom, not milliseconds. Any claim that a learned model performs the active
cancellation has not measured its own latency.

**Secondary-path estimation is the part that gets skipped and should not be.**
`S_hat(z)` is measured once per headset design with a white-noise sweep and
re-checked whenever the mechanical assembly changes. A wrong estimate does not
degrade the loop gracefully — it makes it diverge.

**Lane A can be simulated before any hardware exists.** The iks|PANDAR dataset
provides measured primary, secondary and feedback paths for ANC headphones,
which removes hardware from the critical path for this lane entirely.

---

## 5. Lane B — the signal path

![Signal path detail](../diagrams/5_signal_path_detail.png)

```
 Mic 1 (voice) -----+
                    +--> [1] Audio in --> [2] Aux-IVA --> [3] Normalise --> [4] STFT+ERB
 Mic 2 (reference)--+                                                             |
                                                                                  v
                                                                          [5] Classifier
                                                                          kurtosis -> gamma, beta
                                             +------------------------------+-----------+
                                             v                                          v
                                  [6] Impulsive path                        [7] Neural core
                                      BMRI - detect & fill                      GTCRN - learned mask
                                             |                                          |
                                             +------------------+-----------------------+
                                                                v
                                                      [8] Deep filtering
                                                                v
                                                      [9] Voice guard
                                                                v
                                                     [10] Residual LMS  <--- Mic 2 reference
                                                                v
                                                       [11] ISTFT --> MELPe vocoder --> radio
```

**Mic 3 does not appear in this diagram, and that is the correction.** An earlier
revision of the architecture drove block 10 from the Mic 3 in-ear error signal
and then sent the result to the radio. That cannot work: Mic 3 measures what the
*wearer hears*, and the transmitted voice never passes through the wearer's ear.
Mic 3 and its error loop belong to Lane A. A residual stage in Lane B must be
driven by **Mic 2**, the noise reference — which is Widrow's original two-input
canceller, and is correct.

### [1] Audio input

Reads 128 samples at a time and pushes them into a lock-free ring buffer. Runs on
the audio callback thread at real-time priority, does almost nothing, and never
waits for anything.

**Why it does nothing:** if this thread is ever late, the sound card runs out of
samples and the listener hears a click. It never allocates memory, never takes a
lock, never logs, never throws. Violating any of those produces a click that
appears once every few minutes and is close to undebuggable afterwards.

### [2] Aux-IVA — separating the sources

**Auxiliary-function-based Independent Vector Analysis.** Classical — no neural
network, no training.

It takes the mixed recordings and pulls them apart into separate streams without
being told anything about the sources, by finding the un-mixing that maximises
statistical independence. Unlike plain ICA it keeps each source's frequency bins
tied together, so one source is not scattered across several outputs.

**Why the auxiliary-function variant:** ordinary IVA needs a hand-tuned step size
— too small and it converges too slowly for real time, too large and it becomes
unstable. The auxiliary-function form has **no step size at all** and is
guaranteed to improve at every iteration. That is what makes it usable on a
device.

**What it honestly gives:** separated streams in unknown order (permutation
ambiguity) and unknown scale (scaling ambiguity). It does not label them. That is
fine — all of them are fed to the network, which is what H-GTCRN's ablation found
works best.

### [3] Robust normalisation — the fix that must come first

Audio has to be scaled to a standard loudness before a model sees it. Everyone
does this with **RMS** — average energy.

**RMS is the wrong tool here, and not slightly wrong. It is formally undefined.**

*The practical problem:* a gunshot can be 40 dB above the voice, so the gunshot
sets the scale. Divide by it and the voice is squashed toward the numeric noise
floor — and the scale changes depending on whether a gunshot happened to land
inside the window.

*The formal problem:* impulsive noise is heavy-tailed. For α-stable distributions
with α below 2 the **variance is infinite**. RMS is built on variance. So it does
not merely behave badly here; it does not exist.

**What we use instead**, in order of ambition:

1. **90th-percentile scaling** — take the level 90 % of samples fall below and
   scale by that. One spike cannot move it. Cheap, works, do this first
2. **FLOM** — fractional lower-order moments (Shao & Nikias, 1993). Statistics
   built on a power below 2, which stay finite when variance does not
3. **Causal AGC with a fast-attack limiter** — solves the deployment problem and
   the impulsive problem together

The closest published dual-microphone system uses RMS. This is a real defect in
the nearest prior work, the fix is cited *inside another paper we already hold*,
it takes about half a day, and everything measured downstream is meaningless
until it is done.

### [4] STFT + ERB — turning sound into a picture

**STFT** — Short-Time Fourier Transform. Chops the audio into short overlapping
frames and works out how much energy sits at each frequency in each frame. The
result is a picture: time across, frequency up. Speech looks like stacked
horizontal stripes; a gunshot looks like a vertical wall.

We keep the **complex** form — magnitude *and* phase. Phase matters for
reconstruction quality; discard it and the output sounds smeared and metallic.

> *Caveat worth carrying:* H-GTCRN's own ablation found a magnitude-only
> log-power feature **beat** the full complex feature on its separation branch.
> "Phase is always essential" is too strong a claim for a slide.

**ERB** — Equivalent Rectangular Bandwidth. Instead of hundreds of equal-width
bins, group them into bands that widen with frequency, the way the ear does.
GTCRN is specific: 192 high-frequency bins merged to 64 ERB bands, 65
low-frequency bins left intact, giving a 129-dimensional feature map. The low
bands are preserved because that is where speech harmonics live.

**This is where most of the compute saving comes from.**

### [5] The classifier — the "adaptive" part

A small, fast piece of code that asks of each frame: **steady noise, changing
noise, or a sudden bang?**

It measures **kurtosis** — how "spiky" a signal is. Steady Gaussian noise sits at
3; the Cauchy noise BMRI was validated on measures 27; a gunshot is orders of
magnitude higher. From the answer it sets two dials:

- **γ (gamma)** — how aggressively to clean
- **β (beta)** — the detection threshold

**Why this block is load-bearing:** the problem statement asks for an *adaptive*
system. This is the piece that makes it adaptive. Without it the pipeline behaves
identically for a gunshot and for engine hum, and the word "adaptive" becomes an
assertion. The BMRI paper tunes γ by hand, offline, from a chart. Making it live
is genuinely our change.

**It gives operator modes for free**, because γ has a known relationship to how
much gets removed:

| Mode | γ | Behaviour |
|---|---|---|
| **Listening** | low | Gentle. Keeps ambient sound so the wearer stays aware of the surroundings |
| **Combat** | high | Aggressive. Protects the voice through gunfire, accepts losing ambient detail |

### [6] Impulsive path — BMRI

**Binary Mask Residual Interpolation** (Ruhland et al., 2015). Classical, fast, no
neural component. Two steps:

1. **Split.** A frequency-dependent adaptive threshold — reacting slowly when
   sound rises and quickly when it falls — separates each block into a "target"
   part that is probably signal and a "residual" part that is probably noise
2. **Detect and fill.** An **AR model** (autoregressive — predicting each sample
   from the handful before it) runs over the residual. Where the actual sample
   diverges wildly from the prediction, that sample is an impulse. The worst γ %
   are discarded and **replaced by interpolation** from their neighbours

**Why this path exists at all.** Deep ANC — the main published deep-learning ANC
paper — reduces its own latency by **predicting** the noise a frame or two ahead.
That works for engine hum, which repeats. **It cannot work for a gunshot.** So
this path does not predict. It **waits, detects and reacts**. That is the single
most important architectural decision in the system, and it follows from the
physics rather than from taste.

Cost is small by design: 2048-sample blocks, AR order 16 or 32, one pass.

> **Scope limit.** BMRI was validated on white Cauchy noise at kurtosis 27 —
> gramophone clicks, rain, optical soundtrack noise. Not gunshots. Its SNR
> improvement is around 3.5 dB against a PS target of 15 dB, and it is known to
> *degrade transients* — the paper reports negative improvement on pop music
> because drum sounds trigger the interpolation threshold. Speech plosives are
> transients too. Use it where it fits: the sub-millisecond **ballistic crack**
> and the mechanical layer. For a 50–200 ms muzzle blast, interpolation from
> neighbours is synthesis, not interpolation, and an AR model of order 16–32
> cannot do it. The honest goal there is *conceal and recover*, measured by
> Impulse Recovery Time.

### [7] Neural core — GTCRN

The AI part, and the only learned block in the chain. **GTCRN** — Grouped
Temporal Convolutional Recurrent Network (ICASSP 2024).

It takes the noisy spectrogram and produces a **complex ratio mask** — numbers,
one per band per frame, saying "keep this much of this band", correcting phase as
well as magnitude. Multiply and the noise is gone.

Five tricks make it small enough to run on a headset:

| Trick | What it does |
|---|---|
| **ERB band merging** | 192 high bins compressed to 64 perceptual bands, 65 low bins kept |
| **Grouped convolution** | Split channels into groups processed independently, then shuffled so information still crosses |
| **Grouped RNN** | The same idea applied to the memory part — half the parameters per group |
| **SFE** — subband feature extraction | Unfold each band with its neighbours into the channel dimension |
| **TRA** — temporal recurrent attention | A per-frame energy curve through a small GRU, used to weight moments in time |

**Size:** the paper reports **23.7 K parameters, 39.6 MMAC/s**. The official code
reports **48.2 K parameters, 33.0 MMAC/s** — different accounting. **Quote both**;
a judge who knows the repository will check. For comparison, the closest dual-mic
system is 103 K parameters after pruning.

**Two findings from H-GTCRN worth applying directly:**

- Apply the mask to the **original noisy input**, not to Aux-IVA's cleaned
  output. Separation adds its own distortion, and masking the raw signal avoids
  compounding it
- Feed the network **both** the separated-speech stream **and** the
  separated-noise stream. In H-GTCRN's ablation that was the single biggest
  improvement — bigger than any architecture change

**Published performance, for calibration:** VCTK-DEMAND PESQ 2.87, STOI 0.940,
SI-SNR 18.83 dB. On the DNS3 blind set, DNSMOS BAK 3.90 but SIG 3.00 — against a
noisy-input SIG of 3.20. **It reduces speech quality while improving background
suppression**, which is exactly the over-suppression failure mode this project
exists to make visible.

### [8] Deep filtering

A coarse per-band mask smears fine detail. Voiced speech has harmonic structure —
regular peaks at multiples of the pitch — and one gain per band flattens it,
which is what makes over-processed speech sound robotic.

**Deep filtering** (DeepFilterNet2, IS³) predicts a **small complex filter** that
combines several neighbouring time-frequency points instead of a single gain.
That rebuilds the harmonic structure a plain mask destroys.

Applied only below about 5 kHz, because that is where the harmonics live, and
restricting the band keeps the cost down.

### [9] Voice guard

After the impulsive path fills gaps by interpolation, low-frequency rumble creeps
back in. This stage runs a spectral correction that removes it.

**Why it is a named module and not a footnote:** the problem statement demands
that speech intelligibility be *preserved*. This is the block that guarantees the
cleaning never eats the voice. In the BMRI paper it is a step inside a larger
method; here it is promoted to a module with its own test, because it is the
safety net for the requirement judges will actually check.

### [10] Residual stage — optional, driven by Mic 2

A final classical **LMS** adaptive filter to catch what the learned path leaves.
Cheap, textbook, about twenty lines of code, and it handles slow drift a trained
model cannot anticipate.

**Its reference is Mic 2, not Mic 3.** See the correction at the head of this
section. It is genuinely optional; whether it earns its latency is a measurement,
not an opinion.

### [11] ISTFT

Inverse STFT with overlap-add: each processed frame is windowed and summed into
the output with the same overlap used on the way in, so with the right window and
hop the overlaps sum to exactly one and the joins are inaudible. Because the
complex form was kept throughout, phase is intact and the output does not sound
smeared.

**Perfect reconstruction through STFT → ISTFT with no processing in between is
the third thing to build in the C++ engine, before any DSP.** If that round trip
is not numerically exact, nothing built on top of it can be trusted.

### → And then the part that is not ours

The enhanced waveform does not reach a human directly. A tactical radio transmits
**MELPe** — the NATO STANAG 4591 vocoder — at 2400, 1200 or 600 bits per second.
It does not transmit sound; it transmits a *parametric description* of speech
(pitch, voicing, spectral envelope) and re-synthesises it at the far end.

This matters three ways:

- **The metrics are measured in the wrong place.** PESQ and STOI score the
  denoiser's output; the listener hears the vocoder's output. Artefacts PESQ
  barely notices — musical noise, smeared harmonics, a mis-tracked pitch across an
  interpolated gap — corrupt exactly the parameters MELPe transmits
- **MELPe has its own noise pre-processor.** Two suppressors in series can fight
  each other
- **It is narrowband**, which reopens the question of how much of block 8's
  harmonic reconstruction survives to the far end

**The cheapest original experiment available:** put a vocoder into the evaluation
chain — an open MELPe or Codec2 build is enough — and report every metric
**twice**, before and after. If the ranking of two methods flips across the
vocoder, that single table is a more original contribution than anything else in
the plan.

---

## 6. How the work divides across time

The hard rule: **everything must finish within 10 ms per hop.**

| Thread | Priority | Does | Must never |
|---|---|---|---|
| **Audio callback** | Real-time | Reads and writes 128 samples. Pushes into a lock-free ring buffer | Allocate memory, take a lock, log, throw |
| **Processing** | High | The whole chain, blocks 2 to 11 | Overrun 10 ms |
| **Control** | Normal | Metrics, telemetry, mode switching | Touch the signal path |
| **Lane A loop** | *Separate device* | FxLMS — reference in, anti-noise out | Depend on the application processor |

Two threads for the signal, one for everything else. The processing thread is
separated from the callback so that one slow frame stretches a buffer instead of
dropping audio outright.

**The 10 ms figure is a deadline, not a target.** Miss it and the buffer
underruns, which is heard as a click. This is also why the project reports
**worst-case** frame time rather than the mean: an average of 3 ms with occasional
12 ms spikes fails a 10 ms deadline, and the average hides it completely. Publish
the **99th percentile**.

---

## 7. Timing budget

| Frame / hop | STFT latency | I/O buffer | Total algorithmic | Compute per hop |
|---|---|---|---|---|
| 32 / 16 ms | 32.0 ms | 10.7 ms | 42.7 ms | 16.0 ms |
| **20 / 10 ms — chosen** | **20.0 ms** | **5.3 ms** | **25.3 ms** | **10.0 ms** |
| 10 / 5 ms | 10.0 ms | 5.3 ms | 15.3 ms | 5.0 ms |
| 8 / 4 ms | 8.0 ms | 2.7 ms | 10.7 ms | 4.0 ms |
| **Lane A, for contrast** | — | — | **< 1 ms** | — |

20 / 10 ms was chosen for three reasons: it matches the frame size used by the
closest prior dual-microphone work, so latency and compute comparisons are
like-for-like; 25.3 ms sits inside what radio communication tolerates; and 10 ms
of compute is comfortable.

25 ms would be far too much for hearing your own voice in the earcup, so the
**sidetone path stays analogue** and does not go through the denoiser.

> **An unresolved conflict in this table.** GTCRN and H-GTCRN as published use a
> **32 ms window with a 16 ms hop at 16 kHz**, mapping 192 high bins to 64 ERB
> bands while keeping 65 low bins intact — arithmetic that assumes 257 bins from a
> 512-point FFT at 16 kHz. Choosing 20/10 ms at 48 kHz means the published band
> mapping, the 23.7 K parameter count and the 39.6 MMAC/s figure all stop applying
> and the model must be retrained. At GTCRN's own settings the real algorithmic
> latency is closer to **48 ms than 25.3 ms**. Either choice is defensible;
> claiming both is not. The rate chain — 96 kHz capture, 48 kHz engine, 16 kHz
> neural core, and the anti-alias filters between them — needs to be written down
> and its latency counted.

---

## 8. The innovations, and why each is defensible

| # | What | Why it is ours |
|---|---|---|
| 1 | **Robust normalisation instead of RMS** | RMS is formally undefined for heavy-tailed noise. The closest published system uses it. Half a day to fix, explainable in thirty seconds |
| 2 | **Two paths: predict what you can, react to what you cannot** | Deep ANC's latency trick depends on prediction. Gunshots are unpredictable by definition. Nobody has measured the collapse; the architecture follows from it |
| 3 | **Live classifier tuning γ and β** | BMRI tunes them by hand offline. Making it live is what makes the system genuinely adaptive, which the PS demands |
| 4 | **Three mics serving two lanes** | Lane A needs a reference and an error mic; Lane B needs a primary and a reference. Mic 2 is shared. This is the smallest array that does both |
| 5 | **Input-side clipping model** | Deep ANC models the loudspeaker saturating. Nobody models the microphone saturating — even though a 140 dB blast destroys the waveform before any algorithm sees it |
| 6 | **α-stable augmentation, including the clipped range** | The α-stable authors excluded α < 0.5 because clipping ruined their results. For us clipping *is* the physics. We use the range they threw away, for the reason they threw it away |
| 7 | **Metrics reported twice, across the vocoder** | The listener hears MELPe's output, not ours. Nobody at SIH will have measured this |
| 8 | **Operator-selectable modes** | γ has a known relationship to suppression, so listening mode and combat mode fall out of the existing dial |

---

## 9. The prototype bench

The demonstrated chain contains **no development computer**:

```
   Mic 1 --XLR--+
                +--> Behringer UMC202HD --USB--> Raspberry Pi 5 --audio--> radio
   Mic 2 --XLR--+      2 ch / 24-bit / 48 V       blocks 1-11, ONNX          |
                                                                             |
   Mic 2 --> Lane A loop --> earcup driver <---- received audio -------------+
   Mic 3 -->   (FxLMS)
```

| Part | Why this specific part |
|---|---|
| **Raspberry Pi 5, 8 GB** | Runs Lane B. 8 GB is development headroom, not an inference requirement. Demonstrating on a Pi rather than the Jetson AGX Orin the PS suggests *is* the SWaP-C argument |
| **Official 27 W USB-C PSU** | **Not optional.** The Pi 5 negotiates 5 V / 5 A over USB-PD; a generic charger falls back to 3 A and the board undervoltage-throttles, which presents exactly like a model bug |
| **Official Active Cooler** | **Not optional.** The Pi 5 thermally throttles under sustained inference. Latency figures drift upward over a long run and the measurement becomes worthless |
| **Behringer UMC202HD** | Two channels — a primary at the mouth and a reference on the earcup — with Midas preamps, 48 V phantom and 24-bit conversion. The Pi has no analogue audio input at all |
| **microSD 128 GB A2 ×2** | Two identical images. One is the demonstration card and is never experimented on |
| **Communication unit** | The PS asks for integration with headphones or communication units, so the chain terminates at a radio rather than a screen |

Interactive model: [`../../handbook/zeit-bench-3d.html`](../../handbook/zeit-bench-3d.html).

---

## 10. What is still open

| Item | Status |
|---|---|
| **Target board for Lane A** | The FxLMS loop needs a DSP or microcontroller. Not chosen |
| **Secondary path estimate** | Must be measured once the earcup exists. Until then, simulate from iks\|PANDAR |
| **Mic models** | Unknown. Their maximum SPL decides whether Mic 2 survives a close blast |
| **Aux-IVA cost on our geometry** | Cheap in principle; on three channels at 48 kHz that has to be proved |
| **Frame size conflict** | 20/10 ms at 48 kHz versus GTCRN's published 32/16 ms at 16 kHz. Pick one and re-derive every figure |
| **Clean speech corpus** | Undecided. Blocks training |
| **Whether the residual LMS earns its latency** | Measure it, then decide |
| **Watts on the board** | Nobody in the literature reports it. We should |
