# Two-microphone capture plan

Recording the gunshot **and** the voice at the same time, on two channels, with
one microphone at the gun and one at the speaker.

This replaces the single-microphone plan in [`order.md`](order.md) Stage 1.
Everything else in [`workflow.md`](workflow.md) and [`placement.md`](placement.md)
still holds — this makes the reference-microphone half of it real instead of
simulated.

---

## 1. What this actually is

| | Position | Captures |
|---|---|---|
| **Mic 1 — primary** | With the speaker, at the mouth | Human voice **+** background noise **+** the gunshot as it arrives there |
| **Mic 2 — reference** | Near the gun | The gunshot, direct and loud. **No voice** |

This is **Widrow's two-input adaptive noise canceller**, built with real
hardware instead of simulated. The primary carries signal-plus-noise; the
reference carries noise correlated with the primary's noise but none of the
desired signal.

**Widrow's constraint, restated because everything depends on it:** if Mic 2
contains zero components of the speaker's voice, the adaptive filter is
*mathematically incapable* of cancelling that voice — it minimises total output
power, which forces it to target only the noise.

Put Mic 2 too close to the speaker and the system will eat the voice it exists
to protect. Distance between the two mics is a **requirement**, not a
convenience.

---

## 2. The part that makes this worth doing

Mic 2 sits near the gun. Mic 1 sits with the speaker, some distance away. Sound
travels at roughly 343 m/s.

**So Mic 2 hears the blast before Mic 1 does.**

| Gun-to-speaker distance | Mic 2 leads by | At 48 kHz, 20 ms frames |
|---|---|---|
| 5 m | 14.6 ms | 0.7 frames |
| 10 m | 29.2 ms | 1.5 frames |
| 20 m | 58.3 ms | 2.9 frames |
| 30 m | 87.5 ms | 4.4 frames |

Now put that next to Gap 1.2 from the paper notes.

Deep ANC buys back latency by **predicting** the anti-noise M frames ahead, and
pays 1.5–1.7 dB of cancellation per 10 ms — on *periodic* noise. A gunshot is
unpredictable by definition; there is no information in the milliseconds before
it that says it is coming. That is the whole reason the two-path architecture
exists.

**This geometry sidesteps the problem entirely.** You are not predicting the
gunshot. You are *hearing it early*, because the reference microphone is closer
to the source. At 10 m that is 29 ms of genuine look-ahead, free, with no
cancellation penalty.

That is a physical answer to a problem the literature treats as algorithmic,
and it is the strongest single idea in this plan. It should be measured and
plotted: **cancellation versus gun-to-speaker distance**, showing performance
*improving* with distance where Deep ANC's prediction-based approach degrades.

---

## 3. Three take types, and why the order matters

Do not record everything at once. Three distinct take types, each doing a
different job.

### Type C — gun only, nobody speaks

| Channel | Contains |
|---|---|
| Mic 1 | The gunshot **as heard at the speaker's position** |
| Mic 2 | The gunshot direct at the source |

**Why it is first and most valuable.** Mic 1 in this take is exactly the noise
signal you will mix with clean speech to build training data. Not a synthesised
approximation — the real thing, with the real propagation and the real range
acoustics already baked in.

Mic 1 and Mic 2 together also give you the **source-to-speaker transfer
function**, measured rather than modelled. That is the same quantity the sweep
IR gives you, obtained a second independent way.

### Type B — voice only, no gun

| Channel | Contains |
|---|---|
| Mic 1 | Clean speech, in the real acoustic environment |
| Mic 2 | **Should be near silent** |

Two jobs. It gives clean speech recorded in the actual environment rather than
a studio. And Mic 2 being near-silent is the **direct measurement of Widrow's
isolation constraint** — if Mic 2 picks up the voice here, the geometry is wrong
and the whole approach fails. Better to find that out in this take than after
the shooting.

Record the **same sentences** you will use in Type A. That pairing is what makes
them useful.

### Type A — both at once

| Channel | Contains |
|---|---|
| Mic 1 | Voice **+** gunshot |
| Mic 2 | Gunshot |

The real-world case. This is evaluation data — the thing your system will
actually face — and the real primary/reference pair for the adaptive filter.

**It is not training data,** for the reason in §5.

---

## 4. What you get that nobody else has: a second validation loop

This falls straight out of having all three take types.

Sound pressures add linearly in air. So at Mic 1:

```
        Type B (voice only)  +  Type C (gun only)   ≈   Type A (both)
```

**All three sides are real recordings.** So you can test whether your synthetic
mixing is realistic, using measured data on both sides of the comparison.

Run `analyze.py` on `B + C` and on `A`, compare the 16 metrics, and you are
testing three things at once:

1. **Is additive mixing valid here?** Everyone in speech enhancement assumes it. Almost nobody checks it with real paired recordings
2. **Does your clipping model work?** The mic saturates on the gunshot, so B+C will *not* equal A wherever clipping occurred. The size of that difference *is* a measurement of the saturation — the exact phenomenon Gap 1.5 says nobody models
3. **Is your SNR bookkeeping right?** You know the levels of B and C independently

This is a genuinely publishable-shaped check and it costs you nothing extra —
just the discipline of recording all three types at the same geometry.

**Do this at a minimum of two distances** so the result is not a single point.

---

## 5. The honest problem: clean speech ground truth

Supervised training needs pairs — noisy input, clean target. Type A gives you
the noisy input. **It cannot give you the clean target**, because the voice and
the gunshot are mixed at Mic 1 and no amount of processing separates them
cleanly. That is the problem you are trying to solve, not an input to it.

So:

| Take | Role |
|---|---|
| Type A | **Evaluation only.** Real-world noisy case, and the primary/reference pair |
| Type B | Clean targets |
| Type C | Real noise, at the right position, for mixing |
| **B mixed with C** | **Training pairs** — clean target known exactly, because you made the mixture |

The training set is built from B and C. Type A is what you test against at the
end, and it is the honest test: data you never trained on, recorded as it really
happens.

That is a clean experimental design, and it is stronger than what most of the
papers do — they mix simulated noise and evaluate on simulated mixtures.

---

## 6. What must be verified before the range

### 6.1 Are the two channels actually different?

**This is the one that can silently ruin everything.** When the Digitek was
tested earlier with a single transmitter, the two channels came back
**bit-identical** — maximum difference 0.00. One mono source duplicated into
two channels.

With two transmitters they *should* differ. **But that must be proved, not
assumed.** Speak into one transmitter only and check the two channels diverge.
If they do not, the receiver is summing them into mono, and the entire two-mic
plan collapses to a single microphone with extra steps.

Test this the day before, not at the range.

### 6.2 Are the channels sample-aligned?

Two transmitters, one receiver. If the receiver clocks both from the same ADC,
they are sample-locked and the propagation delay you measure is real acoustics.

If each transmitter has independent latency, part of the delay is radio, not
sound — and the look-ahead number in §2 becomes meaningless.

**How to measure it:** put both transmitters at the *same* place, make a sharp
sound (clap), and measure the sample offset between the channels. It should be
near zero. Whatever it is, that is the fixed radio offset you subtract from
every later measurement.

Do this once, log the number, and repeat it at the end of the session to check
it has not drifted.

### 6.3 Gain must be set per channel, independently

Mic 2 sits near a 140–155 dB source. Mic 1 sits near a speaking voice, maybe
70–85 dB. **That is a 60–80 dB difference.** They cannot share a gain setting.

Set them separately, log both, and never touch either again once shooting
starts — a gain change voids the calibration for that channel.

If the two transmitters share a single gain control on the receiver, Mic 2 must
be moved further from the gun until it fits, and that distance must be logged.

### 6.4 Calibration is per channel

Two channels, two different gains, two different microphones. **Two calibration
tones, two scale factors.** One calibration does not cover both.

### 6.5 Wireless range and interference

Mic 2 is at the gun, Mic 1 is with the speaker, and the receiver is at the
laptop. Check the link holds at the full distance you plan to use *before*
committing to that geometry. Any dropout on the reference channel destroys the
alignment for that take, and the dropout check in `validate.py` will catch it —
but only after the fact.

---

## 7. What changes in the existing toolkit

Nothing conceptual. The pieces already exist; they need to be pointed at two
channels instead of one.

| Tool | Change needed |
|---|---|
| `capture.py` | `--channels 2` becomes the default for shot takes. Take type (A/B/C) recorded in `take.json` |
| `validate.py` | Already has `--array` for two channels. The semantics change: this is **not** a staggered-gain array, it is primary + reference. Mic 2 clipping is a real failure, not an expected one |
| `analyze.py` | Currently mixes to mono. Needs to report per channel, and to report the **inter-channel delay** as a new measured quantity |
| `dsp.py` | Add cross-correlation between channels to measure the arrival-time difference — this is the look-ahead number, and it should be logged per shot |
| Metadata | New fields: `take_type` (A/B/C), `gun_to_mic1_m`, `gun_to_mic2_m`, `mic1_gain`, `mic2_gain`, `radio_offset_samples` |

The **inter-channel delay** becomes a headline measured quantity, alongside the
existing 16. It is the number that proves the look-ahead is real.

---

## 8. Session plan

Assuming two distances and a fixed geometry per block.

| Block | Type | What | Shots | Why |
|---|---|---|---|---|
| 0 | — | Radio offset: both transmitters together, clap ×5 | — | §6.2. Do it first and last |
| 1 | — | Calibration tone, **each channel separately** | — | §6.4 |
| 2 | — | Noise floor, both channels, 60 s | — | Reference for every SNR |
| 3 | — | Range IR (sweep + balloon) | — | Unrecoverable later |
| 4 | **B** | Voice only, ~15 sentences, no gun | — | Clean targets **and** the isolation check |
| 5 | **C** | Gun only, distance 1 | 15 | The noise signal at the speaker's position |
| 6 | **A** | Gun + voice, distance 1 | 15 | Evaluation, and the additivity test |
| 7 | **C** | Gun only, distance 2 | 12 | Second point for propagation |
| 8 | **A** | Gun + voice, distance 2 | 12 | Second point for the additivity test |
| 9 | — | Mechanical, ambience | — | As before |
| 10 | — | Radio offset again, `session.py status`, backup | — | Drift check + completeness |

Blocks 5 and 6 must use the **same geometry** — do not move anything between
them, or the B+C ≈ A comparison is invalid.

---

## 9. Risks, honestly

| Risk | Consequence | Mitigation |
|---|---|---|
| Receiver sums both transmitters to mono | The whole plan collapses | **Test before range day (§6.1)** |
| Independent radio latency per transmitter | Look-ahead number is fiction | Measure the offset, subtract it (§6.2) |
| Shared gain control | Mic 2 clips or Mic 1 is buried | Move Mic 2 further out, log the distance |
| Mic 2 picks up the voice | Filter cancels the speech | Type B takes measure this directly |
| Mic 2 clips on the blast | Reference is useless for that shot | Distance, and per-channel gain. `validate.py` catches it per channel |
| Speaker and gun timing not controlled in Type A | Voice and blast may not overlap | Brief the speaker to talk *continuously* through the shot |

---

## 10. What this buys the project

1. **The reference-microphone architecture stops being simulated.** Every dual-mic paper in the stack simulates the second channel — Tan et al. scale the secondary by a flat −10..0 dB. Ours is measured
2. **Look-ahead from geometry instead of prediction** — a physical answer to Gap 1.2
3. **A second validation loop** (B + C ≈ A) that tests additivity, the clipping model and SNR bookkeeping at once, with real data on both sides
4. **Real evaluation data** — the actual noisy case, never seen during training
5. **Measured inter-channel delay** as a new quantity, per shot

Items 2 and 3 are the ones worth putting in front of a judge. Neither exists in
the literature we have read.
