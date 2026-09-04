# Real gunshot data collection — technical handover

Everything about the **real-data** side of the ZEIT dataset: what is recorded,
how, what is measured from it, and the algorithms behind each step.

Synthetic generation and the DNN are separate stages and are not covered here.

**One rule underneath everything:** we go to the range once. Anything not
captured correctly on the day cannot be recovered afterwards, so the tooling is
built to find problems *at the range*, while a re-shoot is still possible.

---

## 1. Why real data at all

The real recordings are **not** the DNN training set. They are the *reference*
against which the synthetic generator is validated:

```
real gunshots (~60 events)  ──>  validate the generator
                                       │
                                       ▼
                              synthetic generator
                                       │
                                       ▼
                unlimited noise  ──+──  clean speech corpus
                                   │
                                   ▼
                          training mixtures  ──>  DNN
```

The DNN trains on generated audio, which is effectively unlimited. The real set
only has to be big enough to establish a *tolerance* — see §6.

---

## 2. What is recorded

### 2.1 Signal format

| Setting | Value | Reason |
|---|---|---|
| Sample rate | 96 kHz | Gives content to 48 kHz. A gunshot has real energy above 20 kHz; 44.1/48 kHz discards it permanently |
| Bit depth | 24-bit | ~144 dB of range. A gunshot's crest factor is enormous; 16-bit buries the quiet detail |
| Format | uncompressed WAV | Lossy codecs smear transients — the exact thing being measured (§7.4) |
| Limiter / AGC | **OFF** | Compresses the peak, which is the primary measurement |
| Low-cut / HPF | **OFF** | Blast waves have real LF content. Use a windshield, not a filter |
| Channels | 2, staggered gain | One gain cannot span ~100 dB in a single event (§2.3) |

### 2.2 Content captured

| Tier | What | Why |
|---|---|---|
| T0 | Calibration tone (1 kHz, 3 levels) + SPL meter reading | Converts dBFS to Pascals. Without it every level is relative forever |
| T0 | Noise floor, 60 s, mic covered | The reference every SNR is measured against |
| T0 | Range impulse response: sweep ×2, balloon pops ×2 | The range's acoustics. Unrecoverable after leaving |
| T1 | Gunshots: 2 sources × 2 distances × 2 angles | The core reference |
| T2 | Mechanical: bolt, trigger, brass ejection (dry, no live fire) | The quiet sounds the blast normally buries |
| T3 | Range ambience, 5 min | The stationary background |
| T3 | Speech during fire + paired quiet reference | Clean/noisy pairs |

### 2.3 The staggered-gain array

A single gunshot spans roughly 100 dB:

| Component | Approx SPL |
|---|---|
| Muzzle blast peak | 140–155 dB |
| Early reflections | 120–140 dB |
| Reverberation tail | 70–100 dB |
| Bolt, trigger, brass | 55–85 dB |

Set the gain for the blast and the mechanical detail sits in the noise floor;
set it for the mechanical detail and the blast hits the rails. So we record two
channels 18–24 dB apart:

- **ch1 HOT** — captures the tail and the detail. **Expected to clip on the blast.**
- **ch2 COLD** — its only job is to catch the peak unclipped.

`validate.py --array` understands this: clipping on the hot channel is not a
failure as long as the cold channel holds the peak. Without `--array` every
take would fail and the operator would learn to ignore warnings.

---

## 3. How it is recorded

### 3.1 Chain

```
mic --XLR--> [pad] --> preamp / USB interface --> laptop
                          |
                    +48V phantom: condenser needs it, dynamic does not
```

**Microphone choice is the binding constraint.** A 3.5 mm electret tops out
around 100–120 dB SPL; a blank pistol at 1 m is 140–155 dB. Once the capsule
saturates, no pad or gain change downstream recovers the waveform — only
distance helps. Use a **dynamic** mic (moving coil, no active electronics) for
close blast work, and a measurement mic for sweeps and ambience.

### 3.2 Setting gain without live fire

Gain cannot be adjusted mid-string, and an averaging meter under-reads a
gunshot peak by 30 dB or more. Procedure:

1. Gain near minimum, pad ON.
2. Fire a **proxy** (balloon pop / firecracker) at the real distance and angle.
3. Read the true sample peak with `monitor.py` or `record.py --meter`.
4. Target **−18 to −12 dBFS** on the proxy.
5. Back off further for the louder real source.

Too little gain costs noise floor. Too much destroys data permanently. At
24-bit, a −20 dBFS peak is fine.

### 3.3 One command per recording

```bash
python3 capture.py --device "Scarlett" --sr 96000 --channels 2
```

Opens the live monitor (everything shown is being recorded), and on closing the
window asks for a name, files the take in its own numbered folder, and runs the
whole pipeline: validate → slice → measure → plot → report → compressed copy.

**Select the device by name, not by index.** PortAudio indices renumber when
anything is plugged in or removed — a device noted the day before can silently
become a different microphone.

### 3.4 Folder layout

```
DATA/
  001_air-rifle-5m/
      raw.wav          the recording, untouched
      validate.json    GO / NO-GO verdict
      events/          per-shot slices + manifest
      analysis/        features.json + .csv
      report.html
      quicklook/       waveform + spectrogram
      take.json        what this recording was
  _index.md            every recording and its verdict
  _calibration/  _ir/  _plan/  _playback/
```

---

## 4. What is measured

16 quantities per event, plus the session-level and written metadata. These are
the standard descriptors for impulse noise and shooting-range acoustics
(ISO 17201 family), not invented for this project — so the numbers mean
something to a reviewer outside the team.

### 4.1 Level

| Metric | Unit | What it is |
|---|---|---|
| **Peak SPL** | dB re 20 µPa, Z-weighted | The loudest instantaneous pressure. The primary impulse-noise number |
| **SEL** | dB | Total event energy normalised to 1 s. Lets events of different duration be compared fairly |
| **Leq** | dB | Average level over the event window |
| **Crest factor** | dB | Peak ÷ RMS. How tall the peak is |
| **Kurtosis** | — | 4th moment of pressure. How much of the record *is* peak. Gaussian noise = 3; a gunshot is orders of magnitude higher |

Crest factor and kurtosis are not the same claim: one is peak height, the other
is peakiness of the whole distribution.

### 4.2 Time

| Metric | Unit | What it is |
|---|---|---|
| **Rise time** | ms | 10% → 90% of peak on the leading edge. This is what separates a gunshot from a drum hit |
| **A-duration** | ms | The initial positive pressure phase — tied directly to blast physics |
| **B-duration** | ms | Total time the envelope stays within 20 dB of peak. The standard impulse-noise duration measure |

Rise time is the most fragile number here. Muzzle-blast rise is ~10–50 µs; at
96 kHz one sample is 10.4 µs, so the edge is resolved by only a few samples.
This is why the sample rate is not negotiable.

### 4.3 Frequency

| Metric | Unit | What it is |
|---|---|---|
| **1/3-octave spectrum** | dB, 28–31 bands from 25 Hz | **The reference curve.** Everything else in this section summarises it |
| **Spectral centroid** | Hz | Energy centre of mass |
| **95% rolloff** | Hz | Frequency below which 95% of energy lies |
| **Peak frequency** | Hz | Where the most energy sits |
| **Band energy split** | dB ×4 | <100 / 100–1k / 1k–8k / >8k |

### 4.4 Session-level (measured once)

| Metric | What it is |
|---|---|
| **Impulse response** | The range's acoustics. Cannot be measured after leaving |
| **RT60 per octave band** | 62.5 Hz – 8 kHz, T20 and T30 |
| **Direct-to-noise ratio** | Below ~35 dB the RT60 is fitting noise, not decay |
| **Calibration scale** | Pa per full scale, and the SPL at full scale |

### 4.5 Written by hand (no tool can infer these)

`distance_m`, `azimuth_deg`, `mic_height_cm`, `muzzle_height_cm`,
`ground_surface`, `temp_c`, `humidity_pct`, `wind_kmh`, `wind_direction`,
`recorder`, `gain_setting`, source type, ammo, and **`split` (fit / holdout)**.

Geometry determines spreading loss, ground reflection (which produces visible
comb filtering) and directivity. Temperature and humidity determine
high-frequency air absorption — and HF is exactly where synthetic gunshots go
wrong, so without these a mismatch cannot be attributed.

---

## 5. Algorithms

### 5.1 Event detection (`dsp.find_events`)

Locates each shot in a continuous take.

1. **High-pass at 200 Hz.** Without it a wind gust reads as an onset.
2. **Moving-RMS envelope**, 5 ms window / 1 ms hop, computed by cumulative sum
   rather than a framed gather — O(n) with one temporary array. On a 60 s /
   96 kHz file that is ~46 MB instead of ~230 MB, and it is why `validate.py`
   stays inside its time budget.
3. **Adaptive threshold**: `max(floor + 12 dB, peak − 40 dB)`, where the floor
   is the 20th percentile (robust to the events themselves).
4. **Spectral-flux confirmation** in a ±25 ms window around each candidate. A
   real impulse has a broadband spectral jump; a gust or a gain change does not.
   Candidates below a normalised flux of 0.25 are dropped.
5. **Walk back** from the peak to the threshold crossing — that is the true
   onset, and where the cut goes.

Minimum separation 0.30 s. Full-auto bursts need a smaller value and manual review.

### 5.2 Impulse response — sweep (`ir_extract.py`)

Farina exponential sine sweep, 20 Hz → 20 kHz over 10 s:

```
x(t) = sin( ω₁L (e^(t/L) − 1) ),   L = T / ln(ω₂/ω₁)
```

The matched inverse filter is the time-reversed sweep with a −6 dB/octave
amplitude envelope `e^(−t/L)`, normalised so that `conv(sweep, inverse)` peaks
at exactly 1.0. `gen_signals.py` verifies this at generation time and reports
the peak-to-sidelobe ratio (>40 dB required; typically ~54 dB).

Deconvolution is a linear (zero-padded) FFT multiply, then the IR is trimmed to
5 ms before the direct sound.

**Balloon-pop fallback**: direct windowing, no deconvolution, for when wind or
traffic ruins the sweep.

### 5.3 RT60 (`dsp.schroeder_edc`, `rt60_from_edc`)

Schroeder backward integration of the band-filtered IR:

```
EDC(t) = 10 log₁₀ ( ∫ₜ^∞ p²(τ)dτ / ∫₀^∞ p²(τ)dτ )
```

A straight line is fitted between −5 and −25 dB (T20) and −5 to −35 dB (T30),
then extrapolated to 60 dB of decay. r² is reported: below ~0.98 the fit is not
trustworthy. Computed per octave band, 62.5 Hz – 8 kHz.

### 5.4 Calibration (`calibrate.py`)

From the tone recording and the meter reading:

```
p_rms = 20 µPa × 10^(SPL/20)
scale = p_rms / rms_fullscale        [Pa per full scale]
```

Any later file converts as `pressure = sample × scale`. Sanity-checked: a
full-scale SPL outside 100–180 dB is flagged as implausible.

**Changing the recorder gain voids the calibration.** Record a fresh tone.

### 5.5 Quality checks (`validate.py`)

Nine checks, exit code 0 = GO, 1 = NO-GO, 2 = unreadable. Three of them were
harder than they look, and the reasoning is in the code so it does not get
"simplified" away:

**Wind / rumble** — sub-50 Hz energy relative to total, measured *only in the
gaps between impulses*. Gunshots have huge genuine LF content; measuring across
the whole file reports the shot, not the weather. FAIL above −3 dB.

**Handling noise** — LF-only thumps (cable tugs, stand knocks) that a naive
detector reads as shots. Two traps here:

- Thresholding on a low percentile does not work. Low-passing to 100 Hz leaves
  a narrowband signal whose Rayleigh envelope naturally swings over 15 dB; on
  real ambience the envelope crest is ~12 dB while a knock is 60 dB+. So the
  test is crest above the **median**, not above the floor.
- Excluding candidates that align with a detected event does not work either,
  because a loud enough thump *is* detected as an event and excludes itself.
  The honest discriminator is **spectral shape**: measured on this data a
  gunshot sits at −2 to −16 dB LF/HF and a stand knock at +33 dB, so +10 dB
  splits them with ~20 dB of margin either side.

**Bandwidth** — does the file contain the bandwidth its header claims? Found on
real hardware: a 44.1 kHz mic accepted a 96 kHz request and CoreAudio silently
upsampled; the header was correct, every other check passed, and everything
above ~21 kHz was digital zero. Judged by two signatures together:

- *numerical emptiness* — interpolation puts exactly zero energy above the
  original Nyquist, while any real recording has mic and ADC noise filling the
  band to Nyquist;
- *a cliff* — the drop is near-vertical, where a dull source rolls off gently.

Measured here: a real upsample gave −135 dB with a 62 dB cliff; a merely
low-passed but genuine file gave −81 dB and 19 dB. An earlier single-signature
version failed the low-passed file — precisely the false positive that teaches
an operator to ignore warnings.

**Dropouts** — runs of exact digital zero. A real microphone never outputs an
exact zero; there is always self-noise and dither. Exact zeros mean a noise
gate or dropped buffers. Found on a real take: a Bluetooth headset gated 8.3%
of a 33 s recording into silence, including a 580 ms hole, and the file passed
every other check while sounding chopped. FAIL above 1%, or any gap over 50 ms.

The remaining checks are format, clipping (fatal only when it lands on an
impulse), DC offset, noise floor, truncation, and event count vs
`--expect-events`.

---

## 6. How many recordings, and why

`sd` is the tolerance any synthetic generator has to land inside. But `sd` is
itself an estimate, and it is poor when computed from few samples. Verified by
Monte Carlo:

| Shots per condition | How wrong your own tolerance can be |
|---|---|
| 3 | ±46% |
| 5 | ±34% |
| **10** | **±23%** |
| 15 | ±19% |
| 30 | ±13% |

At 3 shots the tolerance is ±46% uncertain — so "it matches" and "it does not
match" are both unfalsifiable. **Never below 10; 15 for the core condition.**

The consequence: **fewer conditions with more repeats beats more conditions
with three shots each.** If time runs short, cut conditions, not repeats.

Allocation for a ~48-shot budget:

- Gun 1: 5 m/90° × **15** (core), 10 m/90° × **12**, 5 m/45° × **9**
- Gun 2: 5 m/90° × **12**
- Balloons ×6, firecrackers ×6 (same geometry, free, and give a backup IR)

Two guns × two distances beats four guns × one distance. Propagation physics is
well understood, so a generator that gets 5 m *and* 10 m right from one model
has captured physics rather than memorised a waveform. A third and fourth gun
add breadth by stealing repeats from the conditions that carry the argument.

---

## 7. Integrity — the parts that protect the claim

### 7.1 Holdout

The metadata CSV has a `split` column, assigned by `plan.py` at planning time,
**before any data exists**. Tuning the generator on all the real data and then
comparing against that same data is circular, and it is the first thing a sharp
reviewer looks for.

### 7.2 Frozen reference

```bash
python3 session.py freeze DATA    # once, after analysis
python3 session.py verify DATA    # before every comparison
```

SHA-256 of every recording, every slice, the measured features — **and of the
measurement engine itself** (`analyze.py`, `dsp.py`, `wavio.py`). Re-running a
modified engine changes the numbers without touching a single audio file; that
is the silent version of the problem, and the one worth guarding against.

### 7.3 Synthetic contamination

`make_test_data.py` produces fake recordings so the tools can be proved to work
before range day. Fake audio is indistinguishable from real audio by inspection:
same extension, same rate, same shape. So every directory it writes is stamped
with `_SYNTHETIC_DO_NOT_USE.txt`, and `ingest.py` / `analyze.py` refuse to touch
marked data (exit code 3). The marker travels with sliced events.

### 7.4 Why the dataset stays WAV

Measured on a real event at 256 kbps AAC:

| | Damage |
|---|---|
| Mid-band levels (31 Hz – 8 kHz) | 0.1 dB — intact |
| Peak, rise time, B-duration | 0.01 dB / 0.00 ms — intact |
| 32 kHz band | **−83 dB — gone** |
| Spectral centroid | **shifted 248 Hz** |

The centroid shift is **173× the real shot-to-shot standard deviation** of
1.43 Hz, and AAC cannot carry 96 kHz at all — it silently downsamples to 48 kHz.
Mid-band and timing survive, which is exactly what makes it dangerous: the files
sound right. Compressed copies live in `_listening/`; measurements always come
from the 24-bit WAV.

---

## 8. What cannot be recovered later

Any *metric* can be recomputed from the raw WAV at any time — spectral flatness,
entropy, kurtosis, 1/6-octave bands, anything not yet invented. The metric list
is not a commitment.

These five cannot:

| | Why | Guard |
|---|---|---|
| **Bandwidth** | If the mic stopped at 20 kHz, 30 kHz never existed | `validate.py` Bandwidth |
| **Absolute level** | No calibration tone → dBFS forever | `session.py status` |
| **Geometry** | Not in the signal | metadata CSV |
| **Range acoustics** | Gone once you leave | `ir_extract.py` |
| **Conditions not shot** | 30 m was never recorded | `plan.py` |

Which means the reviewer's real question is not *"why is metric X missing"* —
we can produce metric X on demand. It is:

> *"Your real data covers 5–10 m. Your generator produces 30 m. How was that validated?"*

The only honest answer is to state the envelope explicitly:

> Validated at 5–10 m, 0–45°, concrete ground, this range's acoustics. Outside
> that envelope the generator is unvalidated.

That is credible. "Everything matched" is what gets taken apart.

---

## 9. Running it

```bash
# once, at home, on the actual range laptop
python3 -m pip install -r requirements.txt
python3 make_test_data.py --out testdata/ && python3 selftest.py testdata/
python3 session.py init --name S1 --out ../DATA --hours 3.5
lpr ../DATA/_plan/RUN_SHEET.txt

# at the range, per recording
python3 capture.py --device "Scarlett" --sr 96000 --channels 2

# before packing up
python3 session.py status ../DATA
python3 session.py backup ../DATA /Volumes/USB
```

`selftest.py` must print **ALL CHECKS PASSED** before range day. It synthesises
deliberately broken recordings — clipped, wind-blown, truncated, buried,
DC-offset, wrong-rate, resampled, gated, knocked-stand — and asserts that
`validate.py` returns NO-GO for each *with the right reason*.

System-wide workflow — architecture, model, training, evaluation, deployment:
[`WORKFLOW.md`](WORKFLOW.md).
Full metric definitions: [`WHAT_WE_MEASURE.md`](WHAT_WE_MEASURE.md).
Tool reference and range-day quickstart: [`README.md`](README.md).
Code: [`../data_collection/`](../data_collection/) — run every command from there.
