# System architecture — ZEIT

The product: a **headset that protects the wearer's hearing, keeps the wearer
aware of the surroundings, and keeps the wearer's voice intelligible on the
radio**, in gunfire, running in real time on embedded hardware.

This is the **final, locked architecture** (locked 19 Sep 2026). It replaces the
earlier Raspberry Pi / 20 ms design. Every other document in the repository
follows this one; where they disagree, this document is authoritative.

- Hardware parts, ports, wiring and the headset build: [`../../synthetic_generator/HARDWARE.md`](../../synthetic_generator/HARDWARE.md)
- Software stack and code layout: [`tech-stack.md`](tech-stack.md)
- Every number the neural network uses: [`../../synthetic_generator/MODEL_VALUES.md`](../../synthetic_generator/MODEL_VALUES.md)
- The training and deployment code: [`../../training/`](../../training/)
- Printable copies with revision pages: `ZEIT_Architecture.docx` and `ZEIT_Hardware.docx` in this folder

Status tags used throughout:

| Tag | Meaning |
|---|---|
| **VERIFIED** | Checked against a published source (datasheet, standard, manufacturer) |
| **MEASURED** | We ran it and have the number |
| **ESTIMATE** | Engineering arithmetic, not yet tested |
| **UNVERIFIED** | A risk; must be checked before relying on it |

Step IDs used here (A1–A11, R1–R5, B1–B11, T1–T8) and hardware IDs (H1–H24)
are shared with `HARDWARE.md`, so the two documents stay aligned.

---

## 1. The problem and the physics that decide the design

A soldier talks on the radio while guns fire nearby. Two people suffer:

- **The wearer** — whose ears are being damaged, and who still needs to hear
  what is around them.
- **The listener at the other end of the radio** — who should hear the order,
  not the gunfire. And, in the other direction, the wearer must understand the
  listener's reply.

PS 26052 asks for an AI/ML-enabled adaptive noise cancellation system for
stationary, non-stationary and impulsive defence noise, with high speech
intelligibility and real-time performance on embedded hardware (DSPs or AI
SoCs such as NVIDIA Jetson, with ONNX / TensorRT), integrated with primary +
reference microphones and headphones / communication units. Targets: SNR > 15 dB,
STOI > 0.85, PESQ > 2.5, low latency.

| Fact | Number | Consequence | Status |
|---|---|---|---|
| Weapons exceed safe limits | Most weapons 150–180+ dBP; MIL-STD-1474E limit at the ear 140 dBP | 10–40 dB must be removed before the eardrum, **even with a flat battery** | VERIFIED |
| Consumer ANC is not built for gunfire | Apple: Hearing Protection not suitable for gunfire or sustained sound above 110 dBA | Consumer ANC cannot be copied and called gunfire protection | VERIFIED |
| Sound crosses an earcup very fast | ≈ 0.3–0.6 ms | Anti-noise electronics must be faster; only a dedicated audio DSP qualifies | ESTIMATE |
| A supersonic bullet's crack arrives before the muzzle blast | Shooter at 30 m: crack 45.2 ms, blast 87.5 ms after firing, **42.3 ms gap** | A free warning the system uses to prepare | ESTIMATE |
| Radio voice tolerates delay | ITU-T G.114: ≤ 150 ms one-way is transparent | The AI has tens of milliseconds; the ear path does not | VERIFIED |

---

## 2. Two lanes

The design is split into two lanes because they have different physics,
different time budgets and different processors. Fusing them makes both
impossible: an AI model that needs tens of milliseconds cannot place
anti-noise at the ear within half a millisecond.

```
   6 MICROPHONES                          PROCESSING                              OUTPUTS

   Mic 2L  outside left   ──┐
   Mic 2R  outside right  ──┤   LANE A — the ear (ADAU1787 DSP + STM32)
   Mic 3L  inside left    ──┼─► hear-through · crack guard · limiter · ANC ──┐
   Mic 3R  inside right   ──┘   both ears, < 1 ms, never waits for the Jetson │
                                         ▲ modes (UART → STM32 → I²C)        ├─(+)─► amp ─► speakers L/R
                                         │                                    │
   Mic 1   boom           ──┐   LANE B — the voice (Jetson Orin Nano Super)   │
   Mic 2R  (2nd copy)     ──┼─► outgoing: 3-input AI (GTCRN, TensorRT) ──────────────► radio TX + PTT
   Mic 4   throat         ──┘   incoming: clean the radio voice (R1–R5) ──────┘
   Radio receive audio    ────► scene classifier → modes for Lane A
```

| | **Lane A — the ear** | **Lane B — the voice** |
|---|---|---|
| Serves | The wearer's hearing and awareness | The listener (outgoing voice) and the wearer's understanding of the reply (incoming voice) |
| Runs on | ADAU1787 audio DSP (H9) + STM32 (H11) | Jetson Orin Nano Super (H15) |
| Time budget | < 1 ms ANC; ≤ 5 ms hear-through | ≤ 150 ms mouth-to-ear; design ≈ 70–85 ms |
| AI | No per-sample AI. Classical DSP; its mode is chosen by Lane B | GTCRN neural network + classical blocks |
| Inputs | Mic 2L, Mic 2R, Mic 3L, Mic 3R | Mic 1, Mic 2R (or 2L, see §3.3), Mic 4, radio receive |
| Outputs | Both speakers (anti-noise + hear-through) | Radio transmit + PTT; incoming radio voice to both speakers |
| Measured by | Noise at a dummy ear (dB reduction), peak at ear vs 140 dBP, 82 dB ceiling | SNR, STOI, PESQ, SI-SNR, IRT, WLPS, latency, watts |
| If it fails | Passive earmuff still protects | Bypass: raw boom mic to the radio |

**Consequence for every claim:** everything the PS measures as SNR / STOI /
PESQ is Lane B. Everything "active noise cancellation" strictly means is
Lane A. Every number quoted must say which lane it belongs to.

---

## 3. The headset

### 3.1 Base

A **3M PELTOR Optime III (H540A) passive earmuff, SNR 35 dB** (X5A, SNR 37 dB,
is the alternative), modified by the team (H1). A passive safety earmuff was
chosen over an aviation headset because:

- it has **no electronics of its own**, so every dB of improvement between
  "system off" and "system on" is demonstrably ours;
- it blocks more sound (SNR 35 vs ~24 dB NRR for budget aviation headsets);
- it is cheap to modify, and a spoiled shell is cheap to replace;
- speakers fitted by us are independent left/right (budget aviation headsets are mono).

The earmuff has a **double casing**: holes for the outside microphones pass
through both layers, and both must be sealed.

### 3.2 The six microphones

```
        LEFT CUP                                RIGHT CUP
   ┌──────────────────┐                    ┌──────────────────┐
   │ [Mic 2L] outside │                    │ outside [Mic 2R] │  ← IM73A135, 135 dB, foam windshield
   │   speaker L      │                    │    speaker R     │  ← 40 mm, 32 Ω
   │ [Mic 3L] inside  │                    │  inside [Mic 3R] │  ← ICS-40180 MEMS breakout, next to the ear
   └────────┬─────────┘                    └──────────────────┘
       boom arm (left, clear of a right-shouldered rifle)
            │
        [Mic 1] 2–5 cm from the mouth                 [Mic 4] throat mic on the neck
```

| Mic | Position | What it hears | Job | Lane | Hardware |
|---|---|---|---|---|---|
| **Mic 1** | Boom, left, 2–5 cm from the mouth | Voice + surrounding noise | The voice that is cleaned and transmitted | B (AI input 0) | H1-B |
| **Mic 4** | Throat (laryngophone) | Voice as neck vibration; almost no airborne noise | Tells the AI where the words are, even during a blast | B (AI input 2) | H4 |
| **Mic 2R** | Outside right cup, opposite the boom | The world, with the least voice | (a) AI noise reference · (b) right feed-forward ANC · (c) right hear-through | A **and** B (AI input 1) | H2 |
| **Mic 2L** | Outside left cup | The world, left side (some voice) | Left feed-forward ANC · left hear-through | A | H2 |
| **Mic 3R** | Inside right cup, next to the ear | What still reaches the right ear | Right ANC error (feedback + checking) | A | H3 |
| **Mic 3L** | Inside left cup, next to the ear | What still reaches the left ear | Left ANC error | A | H3 |

Why the other mics are **not** AI inputs: Mic 2L is on the boom side and
hears too much voice (the AI would learn to remove the voice); Mic 3L / 3R
hear our own speakers (anti-noise, hear-through, radio), not the world.

### 3.3 Handedness switch

The boom sits on the **left** because a right-handed soldier shoulders the
rifle and rests the cheek on the right; 3M's ComTac VIII mounts its speech mic
on the left cup (VERIFIED). For a left-handed soldier the boom moves right,
and the outside mic away from the mouth becomes Mic 2L. A switch on the preamp
board (H6) selects which outside mic feeds AI input 1. Lane A is unaffected;
the model needs no retraining, because it only ever sees "the outside mic away
from the mouth".

### 3.4 Protection chain — passive first

Three walls stand between a gunshot and the eardrum:

1. **The sealed earmuff** — works with no power.
2. **An optional foam earplug** under the earmuff for live fire.
3. **The electronics**, which may only make things quieter or safer. Nothing
   they play into the ear may exceed **82 dB**.

Hearing-protector ratings (SNR, EN 352) are measured **with the electronics
off** — 3M's ComTac VIII datasheet states this (VERIFIED). The design follows
the same rule: protection must not depend on the battery.

| Stage | Level at the ear | Status |
|---|---|---|
| Rifle shot at the head | ~155 dB | ESTIMATE |
| After the sealed earmuff (SNR 35) | ~125–130 dB | ESTIMATE — peaks attenuate differently from the steady-noise rating; measure on the dummy head |
| After earmuff + foam earplug | ~115–120 dB | Double protection adds 5–10 dB (OSHA rule of thumb +5 dB) — VERIFIED rule, ESTIMATE result |
| MIL-STD-1474E limit | 140 dBP | VERIFIED |
| Anything the electronics play | ≤ 82 dB | Design rule, enforced in two places (§4.4, §5.2) |

> **Two meanings of "SNR".** On a hearing protector, SNR is the *Single Number
> Rating* (dB removed). In the speech metrics, SNR is the *signal-to-noise
> ratio* of the transmitted voice (PS target > 15 dB). Never mix them.

> **Scope.** Heavy weapons (180+ dBP) exceed what any headset in this class can
> bring below 140 dBP. The protection claim is for small arms at a distance.

---

## 4. Lane A — the ear

### 4.1 In plain words

The outside microphones listen to the world. Quiet sounds — footsteps, a
colleague — are turned **up**, so the thick earmuff does not make the wearer
deaf to the surroundings. Loud sounds are turned **down**, and nothing is ever
played above 82 dB. When the DSP hears the sharp crack of a bullet, it lowers
the volume **before** the much louder muzzle blast arrives about 40 ms later.
In both ears, ANC plays anti-noise to cancel steady rumble such as engines and
rotors. None of this waits for the Jetson.

### 4.2 One ADAU1787, both ears

The ADAU1787 has **4 ADC inputs and 2 DAC outputs** (VERIFIED, datasheet). A
standard stereo hybrid-ANC headset needs exactly that: one outside and one
inside mic per ear, and one speaker per ear.

| ADAU1787 port | Signal |
|---|---|
| ADC 1 | Mic 2L |
| ADC 2 | Mic 2R (second buffered copy from H6) |
| ADC 3 | Mic 3L |
| ADC 4 | Mic 3R |
| DAC L | Left ear output → H13 amp |
| DAC R | Right ear output → H13 amp |
| I²C | Control from STM32 (via I²C level shifter H12a) |
| Serial port (I²S/TDM) | Mic data to STM32 (via push-pull level shifter H12b) — adaptive ANC phase only |
| USB | SigmaStudio on a laptop — development only |

The chip has two engines: **FastDSP** (up to 768 kHz: biquads, limiters,
volume, mixing — VERIFIED) for everything where microseconds matter, and the
**SigmaDSP** core (28-bit, up to 50 MIPS — VERIFIED) for detection and control.
The same processing path runs twice, once per ear; the SigmaDSP "brain" is
shared, so a crack detected on either side acts on both ears.

```
                 ┌──────────────────────── ONE ADAU1787 ─────────────────────────┐
 Mic 2L (ADC 1) ►│► LEFT:  A1 clip ► A2 band ► A3 level ► A5 limit ──┐           │
                 │         A6 feed-forward ANC ───────────────────────┼► A10 mix ►│► A11 limit ► DAC L
 Mic 3L (ADC 3) ►│►        A7 feedback ANC ───────────────────────────┘           │
                 │                                                                │
 Mic 2R (ADC 2) ►│► RIGHT: A1 clip ► A2 band ► A3 level ► A5 limit ──┐           │
                 │         A6 feed-forward ANC ───────────────────────┼► A10 mix ►│► A11 limit ► DAC R
 Mic 3R (ADC 4) ►│►        A7 feedback ANC ───────────────────────────┘           │
                 │                                                                │
                 │ SigmaDSP (shared): A3 envelopes · A4 crack guard · A1 flags ·  │
                 │                    mode parameter sets (from STM32)            │
                 └────────────────────────────────────────────────────────────────┘
   DAC L/R ──► H13 amp input  (+ incoming radio voice from the Jetson, §5.2) ──► speakers
```

> **To confirm before ordering (Gate 2):** that FastDSP has enough filter
> capacity for both ears' ANC paths at once. The pin count fits exactly; the
> processing capacity is checked in the datasheet or SigmaStudio examples. If it
> is short, ANC filters are shortened; hear-through and limiters are unaffected.

### 4.3 Steps

Each step lists: what it does, the engine, the hardware, timing and status.

**A1 — Clip detection.** Flags samples near full scale on Mic 2L / 2R. Mic 2's
acoustic overload point is 135 dB SPL (VERIFIED, Infineon IM73A135 datasheet),
so a nearby crack **will** clip it. The flag triggers the crack guard (A4) and
freezes ANC adaptation (A8). SigmaDSP · H2, H9 · within a few samples · Designed.

**A2 — Hear-through band filter.** Biquad band-pass ≈ 150 Hz – 6 kHz: keeps
voices, footsteps and vehicles; drops deep rumble and hiss. FastDSP · H9 ·
microseconds · Designed; biquads are native FastDSP blocks (VERIFIED).

**A3 — Level-dependent gain.** Upward expander below ≈ 50 dB (quiet sounds up
to +12 dB), unity in the middle, compressor above ≈ 70 dB. Envelope computed on
SigmaDSP, gain applied on FastDSP; normal sounds change gain over ≈ 5–50 ms.
Behaviour copied from 3M PELTOR ComTac VIII level-dependent mode (VERIFIED).
H9 · < 1 ms signal delay · Designed.

**A4 — Crack guard.** Fast peak + high-frequency-energy detector on Mic 2L / 2R,
also fired by any A1 flag. On trigger: hear-through gain in **both ears** drops
20–30 dB with no attack delay, holds ≈ 300 ms, releases over ≈ 100 ms, and the
mode becomes COMBAT. Uses the crack-before-blast gap: the blast arrives ≈ 42 ms
later. SigmaDSP · H9 · a few samples · Designed (our own idea).

**A5 — Hear-through limiter.** Peak limiter on the hear-through path, calibrated
on the dummy head (§4.5). FastDSP · H9 · microseconds · Designed.

**A6 — Feed-forward ANC.** Filter W(z) on Mic 2L / 2R producing anti-noise before
the noise leaks into the cup; effective on steady low-frequency noise. **Phase 1:
fixed filters** designed in SigmaStudio from the measured acoustic paths of our
earmuff. **Phase 2: adaptive** (A8). FastDSP low-latency path · H2, H9 · must beat
≈ 0.3–0.6 ms · Designed; path VERIFIED, exact end-to-end delay on the eval
board UNVERIFIED.

**A7 — Feedback ANC.** Fixed compensator on Mic 3L / 3R removing leftover
low-frequency noise; loop stability limits it to low frequencies. FastDSP · H3, H9 ·
sub-millisecond · Designed.

**A8 — Adaptation (phase 2).** Filtered-x LMS updates of the A6 coefficients
every few milliseconds. Mic data reaches the STM32 over the ADAU's serial port
(I²S/TDM, through H12b); the STM32 computes new coefficients and writes them
over I²C. The secondary path Ŝ(z) (DAC → amp → speaker → air → Mic 3) is
measured at start-up with a short noise burst. **Adaptation freezes** while A1
or A4 flags an impulse, and while the radio is speaking (RADIO mode), so neither
a gunshot nor the incoming voice can corrupt the filter. STM32 · H9, H11, H12 ·
not in the audio path · Designed; NLMS support in SigmaStudio is reported only
on a forum (UNVERIFIED), so the STM32 route is the plan.

**A9 — Playback removal.** The error signal Mic 3 contains what we play. The
hear-through signal is generated inside the ADAU and is known; it is filtered
by Ŝ(z) and subtracted before A8 uses Mic 3. The **incoming radio voice is added
after the ADAU** (§5.2) and is therefore not subtracted; instead A8 freezes in
RADIO mode, and the fixed feedback loop (A7) is kept below the voice band.
SigmaDSP / STM32 · H9 · Designed.

**A10 — Mixer.** Anti-noise + hear-through per ear, with mode-dependent weights
(§4.6). FastDSP · H9 · Designed.

**A11 — Output limiter.** Brick-wall limiter on each DAC output — the last guard
inside the chip, also against a bug or feedback howl. FastDSP · H9 · Designed.

### 4.4 The 82 dB rule, end to end

The incoming radio voice joins **after** the ADAU, at the amplifier input
(H13). Two limited signals can add, so each path gets part of the budget:

| Path | Limited where | Ceiling at the ear |
|---|---|---|
| ADAU output (anti-noise + hear-through) | A5 + A11 | ≤ 79 dB |
| Incoming radio voice | Jetson R5 | ≤ 79 dB |
| Sum at the speaker | — | ≤ 82 dB |
| Amplifier maximum volume (H13) | Set once during calibration | Locked |

### 4.5 Calibration (once per headset)

1. Fit the headset on the mannequin head (H22) with its in-ear mic on UMC input 4.
2. Play a 1 kHz tone at full scale through the ADAU path; set the H13 volume so the
   ear mic reads 79 dB (checked with the sound level meter, H23). Lock the volume.
3. Repeat through the radio path (Jetson → UMC out 2) with R5 at full scale.
4. Measure Ŝ(z) for each ear (for A6 design and A8).
5. Record the passive attenuation: noise outside vs inside, system off.

### 4.6 Modes (adaptive transparency)

The same blocks, different parameter sets. The mode changes automatically;
the soldier does not touch anything.

| Mode | When | Hear-through | ANC | Who switches |
|---|---|---|---|---|
| **AWARE** (default) | No sustained noise, no impulses | On; quiet sounds up to +12 dB | Gentle, low-frequency | Jetson scene classifier (B5) |
| **COMBAT** | Impulses | Harder compression; ceiling −6 dB; crack guard most sensitive | On; adaptation frozen during each impulse | A4 instantly on a crack; B5 holds it until ≈ 10 s of quiet |
| **VEHICLE** | Loud, steady, low-frequency noise | −10 dB | Maximum | B5 |
| **RADIO** | Incoming radio voice | Ducked −10 dB while the voice plays | On; adaptation frozen | Jetson (R1 detects voice) → STM32 |
| **PASSIVE** | No power, or the ANC button | Off | Off | Physics / STM32 button |

Where the product ideas land:

| Borrowed from | Feature | Here |
|---|---|---|
| 3M PELTOR ComTac VIII | Level-dependent hear-through, 82 dB ceiling, boom on the left | A2, A3, A5, AWARE, §3.3 |
| INVISIO X7 | Passive-first protection rated with power off; body-conducted voice pickup | §3.4, PASSIVE; Mic 4 in B7 |
| Apple AirPods Pro | Adaptive Transparency / Adaptive Audio | Automatic modes; ANC blended with hear-through |
| Ours | Crack guard; adaptation freeze on impulses; AI classifier steering the DSP | A4, A8, B5 → modes |

> **Why Lane A has no neural network.** Apple runs machine learning in the ear
> path on its custom H2 chip (VERIFIED), so it is not physically impossible. We
> do not, because no DSP available to us runs a neural network with a
> sub-millisecond path. Lane A's intelligence comes from Lane B choosing the mode.

---

## 5. Lane B — the voice

### 5.1 In plain words

The soldier's voice is captured twice: by the **boom mic** (clear but full of
gunfire) and the **throat mic** (muffled but almost free of gunfire). The
outside mic records what the noise alone sounds like. Every 16 ms the AI looks
at all three and keeps only the voice from the boom mic. A fast detector warns
when a gunshot starts so a repair step can patch the damaged moment. The
cleaned voice reaches the radio ≈ 70–85 ms after it was spoken. In the other
direction, the teammate's voice arriving on the radio is cleaned of hiss,
levelled and sent to both ears, while Lane A quietens the surroundings.

### 5.2 Incoming radio voice (receive chain R1–R5)

```
Radio speaker out ─► H19 (isolated) ─► UMC in 4 ─► R1 ─► R2 ─► R3 ─► R4 ─► R5 ─► UMC out 2 ─► H13 amp (+ ADAU) ─► speakers
                                                     └─► "voice present" ─► UART ─► STM32 ─► RADIO mode
```

| Step | What it does | Status |
|---|---|---|
| **R1 Capture + voice detect** | UMC input 4 at 48 kHz; energy + voicing detector decides "radio is speaking"; sends RADIO / end-of-RADIO over UART | To write |
| **R2 Hiss / static removal** | Noise gate and spectral subtraction of the radio's channel hiss and squelch tail | To write |
| **R3 Automatic gain** | Levels quiet and loud transmissions to the same listening level | To write |
| **R4 Speech EQ** | Emphasis at 1–4 kHz (where intelligibility lives); small low-frequency lift to offset the feedback ANC | To write |
| **R5 Limiter** | Caps the radio voice at the 79 dB share of the 82 dB budget (§4.4) | To write |

Classical first. A 1-input model from the same training framework can replace
R2 later if the radio channel proves noisy. If the teammate also wears ZEIT, the
voice arrives already cleaned and R2–R5 mostly level and protect it.

### 5.3 Outgoing voice (chain B1–B11)

```
Mic 1 (UMC in 1) ──┐                                           ┌─► B6 impulse repair ─┐
Mic 2R (UMC in 2) ─┼─► B1 capture ─► B3 normalise ─► B4 STFT ──┤                      ├─► B8 merge ─► B9 voice guard
Mic 4 (UMC in 3) ──┘      │                                    └─► B7 GTCRN, 3 inputs ┘                  │
                          └─► B2 impulse detector (arms B6)                                  B10 residual (optional)
                               B5 scene classifier ─► modes to Lane A, γ/β to B6                          │
                                                                                          B11 ISTFT ─► UMC out 1 ─► radio TX
                                                                                                        (PTT keyed by the STM32)
```

**B1 — Capture and resample.** UMC404HD at 48 kHz, 768-sample blocks (16 ms);
stateful 3:1 FIR decimation to 16 kHz. Channels in the locked order: Mic 1,
reference (Mic 2R, or 2L via the handedness switch), Mic 4. Jetson CPU · H6, H14,
H15 · ≈ 16 ms buffer + ≈ 1 ms filter · Resampler MEASURED (1 kHz tone gain 1.000);
the runtime (`training/jetson/realtime.py`) currently takes 2 channels and moves
to 3.

**B2 — Impulse detector.** Peak / kurtosis / high-frequency-energy test on the
reference channel at 48 kHz, before resampling. Timestamps each impulse; arms B6,
informs B5. The crack is known ≈ 18 ms after it happens, ≈ 25 ms before the blast.
To write.

**B3 — Robust normalisation.** Scales by the 90th percentile or a fractional
lower-order moment — never RMS, which is undefined for heavy-tailed impulsive
noise. MEASURED on our 44 real events: RMS drifts 18× within an event, FLOM 5.7×.
Must be applied identically in training (T2) and at runtime. To write in both.

**B4 — STFT + ERB.** 512-point FFT, 256 hop, square-root periodic Hann; 65 low
bins kept, 192 high bins merged into 64 ERB bands (129 features). Built
(`training/zeit/audio.py`, `model.py`); 32 ms algorithmic window.

**B5 — Scene classifier.** Kurtosis + stationarity + level over ≈ 0.5 s →
AWARE / COMBAT / VEHICLE; sets γ and β for B6; sends the mode over UART. Mode
changes in ≈ 30–60 ms (ESTIMATE), not safety-critical. To write.

**B6 — Impulse repair (BMRI).** Binary Mask Residual Interpolation on frames
flagged by B2. Scoped to short cracks (BMRI was validated on white Cauchy noise
at kurtosis 27, not gunshots); long blasts are "conceal and recover", measured by
Impulse Recovery Time. To write.

**B7 — GTCRN, 3 inputs.** The only trained block (§6). Streaming, one 16 ms
frame at a time with carried state, as a TensorRT engine on the Jetson GPU.
MEASURED: 25,109 parameters; streaming = whole-clip to 6×10⁻⁸; ONNX = PyTorch to
5×10⁻⁸; the 2-input version runs 3.9 ms per frame on a laptop CPU. Jetson frame
time UNVERIFIED.

**B8 — Merge.** Crossfades to the B6 output inside impulse windows only. To write.

**B9 — Voice guard.** Restores voice bands if the output falls below what the
throat-mic envelope says was spoken, so cleaning never removes the voice. To write.

**B10 — Residual LMS (optional).** Classical LMS on the reference channel for
slow leftover hum; kept only if it measurably helps.

**B11 — ISTFT and output.** Overlap-add at 16 kHz, 1:3 interpolation to 48 kHz,
UMC output 1 → H19 → radio microphone input. **Push-to-talk is handled by the
STM32, not the Jetson:** the PTT button (H1-G) is read on an STM32 input and the
STM32 drives the H19 optocoupler, then reports "PTT on / off" to the Jetson over
UART. The Jetson's 40-pin header passes through TXB0108 level shifters that
source only ≈ 2–3 mA (VERIFIED, NVIDIA forum) — too little for the optocoupler
LED (≈ 5–10 mA) — whereas an STM32 pin can. PTT, not VOX: VOX would transmit
gunshots. MEASURED: streaming reconstruction error 4.8×10⁻⁷.

**Aux-IVA is not in the chain.** With 2–3 microphones and five or more sources
the separation is underdetermined; the throat mic provides the noise-immune voice
reference more cheaply.

---

## 6. The neural network

### 6.1 Model

| Property | Value | Status |
|---|---|---|
| Architecture | GTCRN (Rong et al., ICASSP 2024), re-implemented, multi-channel input | Built |
| Inputs (locked order) | 0 = Mic 1 boom · 1 = reference (Mic 2R / 2L) · 2 = Mic 4 throat | Locked |
| Features per input | STFT magnitude, real, imaginary → 9 channels; ERB-compressed to 129 bins; subband unfolding → 27 channels | Built |
| Output | Complex ratio mask applied to input 0 (boom) | Built |
| Structure | ERB merge → SFE → 2 conv blocks → 3 grouped temporal conv blocks (dilation 1, 2, 5) with temporal attention → 2 dual-path grouped GRUs → mirrored decoder with skips | Built |
| Parameters | **25,109** (3 inputs) · 24,389 (2) · 23,669 (1 — the paper reports 23.7 K) | MEASURED |
| Audio | 16 kHz, 512 FFT, 256 hop (32 ms window, 16 ms hop) | Locked |
| Streaming | Causal; per-frame state: conv cache (1,6,16,10,33), attention GRU (6,1,16), time GRU (4,33,8) | MEASURED parity |
| Deployment | PyTorch → streaming ONNX → TensorRT FP16, then INT8 | Built for export; TensorRT on Jetson UNVERIFIED |

### 6.2 Why the throat mic, and throat dropout

During a muzzle blast the boom mic can carry 40 dB of gunfire over the voice,
and part of it clips; no mask recovers words that are not in the signal. The
throat mic still carries the rhythm, pitch and low-frequency content of the
words, so the network learns where the voice is. INVISIO uses the same
principle with bone-conduction sensors (VERIFIED). Throat mics are muffled above
roughly 2–3 kHz (ESTIMATE), so the throat channel **guides** the mask on the boom
mic rather than replacing it.

**Throat dropout:** in training, input 2 is set to zero for ≈ 30 % of examples.
The same trained model then works with or without the throat mic — no retraining
if that part fails or arrives late.

### 6.3 What must stay fixed between training and hardware

| Link | Hardware | Training | Status |
|---|---|---|---|
| Input count and order | UMC in 1 / 2 / 3 | Model inputs 0 / 1 / 2 | Locked — label the cables |
| Sample rate | UMC at 48 kHz | 16 kHz | Resampler MEASURED |
| Frame / hop | 768 samples at 48 kHz | 256 at 16 kHz | Parity MEASURED |
| Reference clipping | IM73A135 overloads at 135 dB | Clipping augmentation on input 1 | Built |
| Per-mic gain | H6 gain per channel | Random per-channel gain | Built for input 1; to add for input 2 |
| Voice in the reference | Head between boom and Mic 2R | Delayed, shadowed voice leak −45 … −25 dB | Built; verify with the voice-leak test |
| Throat channel | H4 | Real pairs (TAPS, Vibravox) + simulated channel + dropout | **To implement** in `training/zeit/data.py` |
| Normalisation | B3 at runtime | Same B3 in T2 | To implement in both |
| Speaker leakage into Mic 1 | Sealed earmuff | Assumed negligible | Measure after the build |
| Precision | TensorRT FP16 / INT8 | Compared with FP32 | Tools built |

---

## 7. Training and deployment (offline, on the college supercomputer)

| ID | Step | What happens | Code |
|---|---|---|---|
| T1 | Index | Scan the data drive once: speech, noise, room responses, splits | `build_index.py` — built |
| T2 | Mix fresh examples | Speech + noise at SNR −15 … +20 dB; simulated reference channel (delay, head shadow, tiny voice leak); throat channel (real pair or simulated); throat dropout; B3 normalisation | Built for 2 inputs; throat channel + B3 **to add** |
| T3 | Augment | α-stable gunshot-like bursts (incl. α < 0.5), input clipping, room responses, 20 % Lombard speech, per-channel gain | Built |
| T4 | Train | Loss = 30·complex + 70·magnitude (compressed) + SI-SNR + multi-resolution STFT; AdamW; cosine schedule; early stop on validation SI-SNR | `train.py` — built |
| T5 | Evaluate | SNR out, ΔSNR, SI-SNR, PESQ, STOI per input-SNR bucket; IRT, WLPS; again after a Codec2 / MELPe vocoder | `evaluate.py` — built; vocoder step to add |
| T6 | Prune (optional) | Magnitude pruning, fine-tune, re-evaluate | `prune.py` — built |
| T7 | Quantise | INT8 QDQ calibrated on real noisy recordings; compare with FP32 | `quantize_onnx.py` — built |
| T8 | Export and deploy | Streaming ONNX with parity checks → TensorRT engine on the Jetson → live runner | `export_onnx.py`, `jetson/` — built for 2 inputs; 3-input export MEASURED |

Order: a single-channel sanity run on VoiceBank-DEMAND must reach PESQ near the
paper's 2.87 before the full 3-input run.

---

## 8. How the two lanes connect

| Link | From | To | Carries |
|---|---|---|---|
| Shared microphone | Mic 2R via H6 (two buffered copies) | ADAU ADC 2 and UMC in 2 | Same noise reference, neither board loading the other |
| Modes down | Jetson (B5, R1) — UART | STM32 → ADAU (I²C via H12a) | AWARE / COMBAT / VEHICLE / RADIO parameter sets |
| Status up (optional) | ADAU → STM32 → UART | Jetson | Crack events, current mode, for the live display |
| Incoming radio voice | Jetson R5 → UMC out 2 | H13 amp input, summed with ADAU output | Cleaned teammate voice to both ears |
| Outgoing voice | Jetson B11 → UMC out 1 | H19 → radio microphone input | Cleaned wearer voice |
| Push-to-talk | PTT button → STM32 input; STM32 → H19 optocoupler | Radio PTT | Transmit on / off; STM32 reports it to the Jetson |

### UART protocol (Jetson ↔ STM32)

115200 baud, 8N1, 3.3 V, one ASCII line per message, newline-terminated.

| Direction | Message | Meaning |
|---|---|---|
| Jetson → STM32 | `MODE AWARE` / `MODE COMBAT` / `MODE VEHICLE` | Scene mode from B5 |
| Jetson → STM32 | `RADIO 1` / `RADIO 0` | Incoming radio voice present / ended (R1) |
| STM32 → Jetson | `PTT 1` / `PTT 0` | Soldier pressed / released push-to-talk |
| STM32 → Jetson | `CRACK` | Crack guard fired (for the live display and logs) |
| STM32 → Jetson | `ACK <mode>` | Mode applied to the DSP |
| Both | `PING` / `PONG` | Link check every second; if the Jetson stops answering, the STM32 keeps the last mode |

**Design rule:** nothing that protects the ear depends on the Jetson. If the
Jetson crashes, Lane A keeps its last mode; the crack guard and limiters still
work; the passive earmuff still protects.

At power-on the STM32 loads the DSP program into the ADAU over I²C (exported
from SigmaStudio). If the eval board supports self-boot from its own memory
(to confirm in UG-1532), that is used instead.

---

## 9. One gunshot, millisecond by millisecond

Rifle 30 m away, supersonic round, AWARE mode, soldier speaking. All ESTIMATE.

| Time | Where | What happens |
|---|---|---|
| 0 ms | Rifle | Trigger; muzzle blast travels at 343 m/s; the bullet travels faster |
| 36.5 ms | Bullet, ~3 m away | Closest approach; the crack shockwave forms near the soldier |
| 45.2 ms | Mic 2L, Mic 2R | Crack arrives; Mic 2R likely clips (135 dB) |
| 45.2 ms + µs | Lane A | A1 + A4: hear-through −20…30 dB in both ears; A8 frozen; mode → COMBAT |
| ≈ 61–63 ms | Lane B | The block containing the crack reaches the Jetson; B2 flags it; B6 armed; B5 confirms COMBAT |
| 87.5 ms | Head | Muzzle blast. The earmuff (+ earplug) takes the peak; hear-through already ducked and capped |
| 87.5–300 ms | Lane B | GTCRN masks the boom mic guided by the throat mic; B6 patches short destroyed parts |
| ≈ 350–450 ms | Lane A | Crack guard releases smoothly; adaptation resumes |
| +10 s quiet | Both | B5 returns to AWARE |

---

## 10. Latency

**Lane A**

| Path | Limit | Design |
|---|---|---|
| ANC (A6) | ≈ 0.3–0.6 ms acoustic path | FastDSP up to 768 kHz (path VERIFIED; end-to-end UNVERIFIED) |
| Hear-through (A2–A5) | ≤ 5–6 ms before it sounds coloured (hearing-aid delay studies, VERIFIED) | Well under 1 ms (ESTIMATE) |
| Crack guard (A4) | Before the blast, ≈ 42 ms after the crack | A few samples (ESTIMATE) |
| Mode change | Hundreds of ms acceptable | ≈ 30–60 ms (ESTIMATE) |

**Lane B — mouth to radio**

| Step | Delay | Status |
|---|---|---|
| Interface input buffer | ≈ 16 ms | ESTIMATE |
| Resampling down and up | ≈ 2 ms | ESTIMATE |
| STFT window | 32 ms | By design |
| Compute per frame (must fit in 16 ms) | ≈ 2–6 ms | 3.9 ms MEASURED on a laptop CPU (2-input); Jetson UNVERIFIED |
| Interface output buffer | ≈ 16 ms | ESTIMATE |
| **Total** | **≈ 70–85 ms** | ESTIMATE |
| ITU-T G.114 one-way limit | ≤ 150 ms | VERIFIED |

The incoming radio voice (R1–R5) adds ≈ 20–40 ms (ESTIMATE), unnoticeable when
listening to a radio.

---

## 11. Failure behaviour

| Failure | Wearer gets | Listener gets |
|---|---|---|
| Battery / power lost | Passive earmuff protection | Nothing (radio off) |
| Jetson crash | Lane A in its last mode; crack guard and limiters work | Nothing until restart (bypass switch optional) |
| ADAU fault | Passive protection; radio voice still reaches the ears through H13 | Unaffected |
| Mic 2 clipped | Crack guard + frozen adaptation | Model trained on clipped references |
| Throat mic missing | Unaffected | Model continues on 2 inputs (throat dropout) |
| Mic 3 failed | ANC in that ear stops; hear-through works | Unaffected |

---

## 12. Prototype versus fielded unit

The bench prototype uses development boards so every stage can be measured.
The fielded design is the same architecture, shrunk:

| Bench prototype | Fielded unit |
|---|---|
| ADAU1787 evaluation board, STM32 Nucleo | ADAU1787 chip + small STM32 on one PCB inside the right earcup (tentative 34 × 26 mm layout: `presentation/make_pcb.py`) |
| UMC404HD USB interface | An audio codec on the Jetson carrier, over the Jetson's I²S pins |
| Jetson developer kit | Jetson Orin Nano module on a small carrier in a chest-mounted unit, the same form factor as existing tactical headset control units |
| Mains / power bank | Radio battery or a vest battery; Jetson in its 7 W mode |

---

## 13. Proven versus designed

**Proven — we have the numbers**

| Claim | Evidence |
|---|---|
| RMS normalisation fails on gunshots | MEASURED on 44 real events: RMS drifts 18×, FLOM 5.7× within an event |
| Impulse Recovery Time exposes damage PESQ / STOI hide | MEASURED: the 1–2 kHz band takes 464 ms to recover |
| Our own impulsive recordings | Range trip 7 Sep 2026: 15 takes, 213 events, 44 true impulses (air gun, uncalibrated) |
| The model and deployment path work | MEASURED: 25,109-parameter 3-input model, streaming and ONNX parity ≤ 6×10⁻⁸; 3.9 ms/frame (2-input) on a laptop CPU; 12/12 self-test |
| Consumer ANC excludes gunfire | VERIFIED: Apple Hearing Protection documentation |

**Designed — parts verified, system not yet built**

| Claim | Verified so far |
|---|---|
| Two lanes on one headset | ADAU1787 ANC-oriented low-latency path; Jetson TensorRT platform |
| Both-ear hybrid ANC on one DSP | 4 ADC / 2 DAC matches a stereo hybrid-ANC headset |
| Crack guard | Physics; DSP detector capability |
| 3-input AI with a throat mic | Body-conducted voice rejects airborne noise; paired datasets exist |
| Peltor-style hear-through and automatic modes | 82 dB practice; limiter blocks native to the DSP |

---

## 14. Gates and open checks

**Before ordering**

| # | Check | Affects |
|---|---|---|
| 1 | EVAL-ADAU1787Z user guide (UG-1532): built-in USB? I/O voltage / level shifting? self-boot? serial-port pins? analog input connectors and mic-bias? | H10, H11, H12 |
| 2 | ADAU1787 FastDSP capacity for two ANC paths | H9 |
| 3 | IM73A135 available as a ready breakout in India | H2 |
| 4 | Earmuff price and cup depth (40 mm speaker + inside mic must fit) | H1 |
| 5 | PMR446: WPC ETA certificate, K-type accessory jack, its pinout | H18, H19 |
| 6 | Written Jetson quote | H15 |

**After arrival**

1. UMC404HD records 4 channels on the Jetson.
2. The 3-input model builds as a TensorRT engine (GRU layers convert); frame time < 16 ms.
3. Voice-leak test: the reference mic hears ≥ 25 dB less voice than Mic 1.
4. Hum check: grounding first; isolation only if needed.
5. Hear-through + limiters in SigmaStudio, then fixed ANC, then adaptation.
6. Throat-mic spectra: simulated vs real on held-out pairs.
