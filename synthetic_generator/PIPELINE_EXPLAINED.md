# The pipeline, explained — answers for when someone asks

Written to be defended out loud. Every number here comes from our own data.

---

## Q1. What is real and what is synthetic?

Three different things, and people mix them up constantly.

| | What it is | Where it comes from | Stored? |
|---|---|---|---|
| **Clean speech** | the thing we want to keep | downloaded corpus (LibriSpeech, VCTK, SPRING-INX, Lombard GRID) | yes, ~30 GB |
| **Noise** | the thing we want to remove | **our 44 measured gunshots** + downloaded corpora (MAD, MUSAN, NOISEX-92…) | yes, ~135 GB |
| **Training mixtures** | clean + noise at a chosen SNR | **generated on the fly, in the dataloader** | **no** |

The equation, run fresh for every batch:

```
noisy = clean_speech  +  g · (noise ⊛ RIR)

where g is chosen so that  SNR = 10·log10( P_speech / P_noise )
```

The model sees `noisy`, is asked to output `clean_speech`. That is the whole
supervision signal — and it is free, because we built the mixture ourselves and
therefore already know the answer.

**Nothing about the mixture is stored.** Only the fixed validation and test sets
are written to disk (~5 GB), because those must be byte-identical across every
experiment or the comparisons mean nothing.

---

## Q2. "We only recorded gunshots — don't we need background noise too?"

**The gunshot *is* the noise.** That is the part that flips people around.

We are not building a gunshot detector. We are building a denoiser for speech.
So in our data:

- the **signal** is a human voice — and it comes from a speech corpus, not from
  the range
- the **noise** is the gunshot — and that is what the range trip captured

So the 44 events are a **noise library**, not recordings-with-noise-in-them.

And this is why we *want* them as isolated as possible. If a gunshot recording
already had traffic and wind mixed into it, we could never control the mix — we
would be stuck with whatever ratio happened on the day. Recorded clean, we can
add traffic at exactly −6 dB, wind at exactly −12 dB, and vary it per batch.

**One thing we do want baked in: the range's own reverb.** That is real
propagation through a real space, and it is not noise contamination — it is part
of what a gunshot *is* at that distance. That is also why the range IR matters.

So: yes we need background noise — but it comes from MUSAN, DEMAND, TAU and
NOISEX-92, added under our control, not from the range recordings.

---

## Q3. "shot01 is 15 seconds — why only 2 events?"

Because only two things in those 15 seconds were more than **12 dB** above the
background. That is the detector's default prominence threshold.

Measured on `DATA/002_shot01/`:

| | |
|---|---|
| Recording | 15.06 s, 48 kHz, 24-bit, 2 channels |
| Noise floor | −49.44 dBFS |
| EVENT-001 | onset 5.433 s, peak −5.88 dBFS, **SNR 43.6 dB** |
| EVENT-002 | onset 9.236 s |

Lower the threshold and more appear — but look at what they are:

| Prominence | Events found |
|---|---|
| 20 dB | 2 |
| 15 dB | 2 |
| **12 dB (default)** | **2** |
| 10 dB | 4 |
| 8 dB | 5 |
| 6 dB | **15** |

At 6 dB you get 15 "events" in 15 seconds — roughly one per second. Those are
echoes, the tail of the previous shot, handling, footsteps. They are not shots.

**SNR 43.6 dB is the number that matters.** That is an exceptionally clean
isolated impulse. Two events at 43 dB SNR are worth far more than fifteen at
6 dB, because every one of them will be mixed against 900,000 speech segments —
a dirty event contaminates every mixture it touches.

If you want more events per take, the fix is at the range, not in software:
fire more shots per recording, and leave 3 s of silence between them.

---

## Q4. "Why did you only give me images?"

The images are the *check*, not the output. Each per-shot folder has:

```
002_shot01/
  raw.wav                  the full 15 s take
  events/EVENT-001.wav     the sliced impulse  <- this is the data
  events/EVENT-002.wav
  events/manifest.json     onset, peak, SNR, clipping, truncation per event
  analysis/shot01.json     the 16 measured attributes per event
  analysis/shot01.csv      same, as a spreadsheet
  quicklook/EVENT-001.png  waveform + spectrogram, so a human can eyeball it
  quicklook/contact_sheet.png
  validate.json            the ten GO/NO-GO checks
```

The WAVs are the dataset. The PNGs exist because eyes catch things no automatic
check does — a doubled report, a ricochet, someone talking over a shot.

---

## Q5. Which attributes do we actually use?

`analyze.py` measures these per event. They are the standard impulse-noise
metrics, deliberately chosen so the numbers mean something to an acoustician
outside this project.

### Level
| Attribute | Meaning |
|---|---|
| `peak_db` | peak level |
| `sel_db` | Sound Exposure Level — total energy |
| `leq_db` | equivalent continuous level |

### Temporal shape — this is what makes an impulse an impulse
| Attribute | Meaning | Our median |
|---|---|---|
| `rise_time_ms` | onset to peak | 9.4 ms |
| `a_duration_ms` | the classic impulse metric — first pressure excursion | **0.27 ms** |
| `b_duration_ms` | decay to −20 dB, i.e. the reverb tail | 342.7 ms |
| `crest_factor_db` | peak ÷ RMS | 17.9 dB |
| `kurtosis` | fourth moment — how heavy the tails are | **18.5** |

### Spectral
| Attribute | Meaning | Our median |
|---|---|---|
| `centroid_hz` | spectral centre of mass | 1415 Hz |
| `rolloff95_hz` | where 95 % of energy is below | 4471 Hz |
| `peak_freq_hz` | loudest frequency | 592 Hz |
| 1/3-octave spectrum | the full band-by-band picture | — |

**Why kurtosis and crest factor matter most:** a Gaussian signal has kurtosis 3.
Ours is 18.5. That single number is what the classifier uses to decide "this
frame is impulsive, switch to the transient path". It is the adaptive element of
the whole architecture.

### For the model itself, the input features are different
Not these scalars — the network sees a **complex STFT**, ERB-compressed to 129
bands (64 ERB from 192 high bins + 65 low bins kept as-is), magnitude *and*
phase. The scalars above are for **validating that synthetic matches real**.

---

## Q6. How do we do normalisation?

### The short version
**Percentile (90th) or fractional lower-order moments. Never RMS.**

### Why never RMS — this is the strongest technical point in the project

RMS is a second moment: `sqrt(E[x²])`.

Impulsive noise is modelled by **α-stable distributions**. For any α < 2, the
second moment of an α-stable distribution is **infinite**. So `E[x²]` does not
converge. Compute an RMS over a gunshot and you do not get a stable number — you
get whatever the loudest sample in your window happened to be. Take a longer
window and the answer changes. Take a different take and it changes again.

Normalising by a quantity that does not converge means every training example is
scaled by a random number.

This is not theoretical: it is a real defect in the closest prior system to ours,
and fixing it is roughly half a day of work.

### What we do instead

| Method | How | Why it works |
|---|---|---|
| **90th-percentile** | scale by the 90th percentile of \|x\| | order statistics are finite for any distribution, α-stable included |
| **FLOM** | scale by `E[\|x\|^p]^(1/p)` with `p < α` | fractional lower-order moments converge where the second moment does not |

Both are computed **per utterance, before the STFT**, and the scale factor is
stored so the output can be scaled back.

### And on the output side
The mask is applied to the **noisy input**, not to a pre-separated estimate.
That is H-GTCRN's ablation finding, and it means normalisation errors do not
compound through the separation stage.

---

## Q7. What SNR do we train at?

| Range | Why |
|---|---|
| **−12.5 to −2.5 dB** | what gunfire actually produces; H-GTCRN's regime |
| 0 to +20 dB | the literature's normal range |

We train across both and **report as a curve against input SNR**, not as a single
number. The PS asks for SNR > 15 dB; nothing in our fifteen papers reaches that,
and the best published result is 8.61 dB. Reporting a curve and stating where we
cross is defensible. Reporting one number is not.

---

## Q8. So what is actually generated, and how much?

With the core corpora:

```
900,000 speech segments × 135,000 noise segments
        × 8 SNR levels × 50 RIRs × 5 α values
= 2.4 × 10^14 distinct mixtures
```

We will never see more than a few million of them during training. The point is
that the dataset is not the bottleneck — compute is. That is why the 44 real
events are enough: each one gets combined with hundreds of thousands of speech
segments under hundreds of conditions.

**Downloaded: ~28 GB to start, ~165 GB for everything.
Generated: 10^14 mixtures, of which ~5 GB is ever written to disk.**
