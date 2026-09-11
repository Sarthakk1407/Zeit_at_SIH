# Phases — what happens in what order

Derived from `order.md`. Each phase names what it needs, what it produces, and
what it unblocks. **Nothing here can be reordered without breaking a
dependency.**

Status: ✅ done · 🟡 in progress · ⬜ not started · 🔴 blocked

---

## Phase 0 — Foundations

### 0a. Real-data collection toolkit ✅
21 CLI tools, self-test green, calibration to Pascals, range IR, nine quality
checks, session freeze with checksums of data **and** measurement engine.
→ **Unblocks:** Phase 1

### 0b. Baseline reproduction ⬜
Reproduce Deep ANC, GTCRN, H-GTCRN, BMRI numbers on their own published data.
Needs no hardware, no range data.
→ **Unblocks:** Phase 2 (you cannot show a collapse without a baseline)

### 0c. Public noise corpora ⬜
Download per `DATASET_SPEC.md` §2. Gunshots come from **our** range trip;
everything else comes from here.
→ **Unblocks:** Phase 2 grid, Phase 4 mixtures

### 0d. Clean speech corpus 🔴 **BLOCKED — decision needed**
`order.md` calls this *the largest open item in the dataset plan*. It sets
training-set size; nothing downstream can be sized until it is made.
Recommendation in `DATASET_SPEC.md` §3 — LibriSpeech + VCTK + EARS +
Common Voice Hindi + **Lombard GRID (≥20 %)**.
→ **Blocks:** Phase 4 entirely

---

## Phase 1 — The real reference ✅

Range trip done 7 Sep 2026. Air gun, target impact as the impulsive source.

| Produced | |
|---|---|
| Recordings | 15 takes, 2-channel, 48 kHz / 24-bit |
| Sliced events | 213 |
| Clean-channel subset | 28 |
| **True impulsive events** | **44** |
| Per-event metrics | `REFERENCE_REAL/analysis/*.json` + `.csv` |
| Statistics | `stats_all` / `stats_clean` / `stats_impulse` |
| Reports | `report_impulse.html`, `report_clean.html` |

**Known limits, state them honestly:**
- **Uncalibrated** — no 1 kHz tone was recorded, so levels are dBFS not dB SPL.
  No peak-overpressure or Friedlander claims are possible from this trip.
- **Air gun, not firearm** — target impact is a metallic transient, not a
  140–155 dB muzzle blast with low-frequency blast energy. This validates the
  pipeline; it is not the gunshot dataset.
- **Channel 2 degraded** — MacBook mic clipped (+7…+13 dBFS) and macOS gating
  produced digital-silence runs, so the two-mic delay / look-ahead measurement
  did not survive. Channel 1 (wireless lav) is clean on 8 of 15 takes.

→ **Unblocks:** Phase 3

---

## Phase 2 — Baseline collapse ⬜

The two findings the whole story rests on. No hardware, no range data needed.

| Step | What | Effort |
|---|---|---|
| 2.1 | Robust normalisation — percentile / FLOM vs RMS | half a day |
| 2.2 | The impulsive evaluation grid | days |
| 2.3 | Latency vs prediction horizon (NMSE vs M, stationary **and** impulsive on one chart) | days |

→ **Unblocks:** Phase 3 (you must know what you are fixing)

---

## Phase 3 — Synthetic generator ⬜

Needs Phase 1 (reference) and Phase 2 (know the target).

| Step | What | Produces |
|---|---|---|
| 3.1 | Blast model, range-IR convolution, distance / propagation | synthetic gunshots |
| 3.2 | Measure with **`analyze.py` — the same engine** | `features.json` |
| 3.3 | Compare against the real **holdout** split | per-band deltas, log-spectral distance |

**Two non-negotiables:** same measurement engine (else part of any difference is
a difference in the measuring), and holdout-only comparison (else it is
circular).

→ **Output:** the dataset-quality claim — the thing shown to judges.

---

## Phase 4 — Training data 🔴 (blocked by 0d)

| Step | What |
|---|---|
| 4.1 | Mix clean speech × noise across SNR, **including −12.5 to −2.5 dB** |
| 4.2 | α-stable augmentation, α ≈ 1, multiple separate values |
| 4.3 | **Below α = 0.5 and let it clip** |
| 4.4 | Input-side saturation model |
| 4.5 | Structured bursts, not i.i.d. spikes |
| 4.6 | Wide RIR spread — near-anechoic → hard-walled |
| 4.7 | HRTF head shadow, not a flat scalar |

---

## Phase 5 — Model ⬜

| Step | What |
|---|---|
| 5.1 | Neural core: GTCRN-class — ERB, grouped conv/RNN, SFE, TRA, complex |
| 5.2 | Transient path: BMRI-style AR detect + interpolate |
| 5.3 | Adaptive element: kurtosis classifier tuning γ and β |
| 5.4 | Intelligibility guard: spectral correction after interpolation |
| 5.5 | Optional LMS residual stage |
| 5.6 | Train, then evaluate on the Phase 2 grid |

---

## Phase 6 — Edge ⬜

ONNX export → quantisation → pruning → measure latency **and power** on the
real board. Power is a free differentiator: nobody in the literature reports it.

---

## Phase 7 — The extra experiment ⬜

IRT (Impulse Recovery Time) and WLPS (Words Lost Per Shot) — ~50 lines each,
no hardware, no trained model. PESQ and STOI average over an utterance, so a
200 ms gunshot barely moves them; these two metrics measure exactly the damage
this PS is about. Cheapest original contribution available.

---

## Critical path

```
0a ✅ ─→ 1 ✅ ─┐
0b ⬜ ─→ 2 ⬜ ─┴─→ 3 ⬜ ─→ 4 🔴 ─→ 5 ⬜ ─→ 6 ⬜
0c ⬜ ────────────────────↑
0d 🔴 ────────────────────┘
```

**The one decision that unblocks the most: 0d.** It is a choice, not work.
