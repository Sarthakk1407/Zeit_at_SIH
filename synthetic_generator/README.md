# synthetic_generator

Everything for the dataset pipeline, the model, and the evidence behind both.

**Status as of 12 Sep 2026:** data collection essentially done — **11 datasets,
~229,000 audio files, ~100 GB** on the SSD, plus our own 44 measured impulsive
events. Phase 1 (real reference), Phase 2.1 (robust normalisation) and Phase 7
(IRT + WLPS) are complete. Phase 3 (synthetic generator) is next.

---

## Read these first

| File | What it answers |
|---|---|
| **`PIPELINE_EXPLAINED.md`** | *How does the whole thing actually work?* — 8 questions answered from our own numbers, written to be defended out loud |
| **`GLOSSARY_HINGLISH.md`** | *What do these words mean?* — 33 terms in Hinglish with everyday examples |
| **`PHASES.md`** | *What order does it happen in?* — Phases 0–7 with dependencies and status |
| **`CHECKLIST.md`** | *What is done, what is left?* — tick as you go |

## Reference

| File | What it holds |
|---|---|
| **`DATASET_SPEC.md`** | 20 noise classes, every corpus, clean speech, RIRs, HRTFs, sizes, licences |
| **`MODEL_VALUES.md`** | Every number the model needs — STFT/ERB, architecture, training, SNR range, augmentation, evaluation targets, edge |
| **`HARDWARE.md`** | The bench: 3-mic headset, Behringer UMC202HD, Pi 5, sensor positions, the 42.3 ms look-ahead timing |
| **`STORAGE.md`** | How much is downloaded vs generated, and how big an SSD you need |
| **`DOWNLOAD.md`** | Every dataset's download URL, in priority order |
| **`DATA_SOURCES.md`** | Auto-generated: what is actually on the drive right now, and where each piece came from |

## Tools

| Script | What it does |
|---|---|
| **`download.py`** | Downloads the corpora that have direct URLs. Resumable, parallel, pause/resume keys, auto-extract, rename-proof folder lookup |
| **`unpack_manual.py`** | Extracts whatever you downloaded by hand; flattens nesting, files the archive under `_archive/` |
| **`mat_to_wav.py`** | NOISEX-92 ships as MATLAB `.mat` — this turns it into WAV |
| **`make_manifest.py`** | Scans the drive and regenerates `DATA_SOURCES.md` |
| **`metrics/irt.py`** | **IRT — Impulse Recovery Time.** How long each band takes to come back after an impulse |
| **`metrics/wlps.py`** | **WLPS — Words Lost Per Shot.** Word errors inside the impulse window |
| **`experiments/p1_normalisation.py`** | Measures that RMS does not converge for α-stable noise, while percentile and FLOM do |

## Commands

```bash
# download what can be downloaded automatically
python3 synthetic_generator/download.py "/Volumes/ZEIT V.1.0"

# extract anything fetched by hand
python3 synthetic_generator/unpack_manual.py "/Volumes/ZEIT V.1.0/zeit-data"

# refresh DATA_SOURCES.md
python3 synthetic_generator/make_manifest.py "/Volumes/ZEIT V.1.0/zeit-data"

# the two results we already have
python3 synthetic_generator/experiments/p1_normalisation.py \
        --events "data for training/REFERENCE_REAL/events_impulse"
python3 synthetic_generator/metrics/irt.py \
        "data for training/REFERENCE_REAL/events_impulse"
```

---

## Where the real data lives

```
/Volumes/ZEIT V.1.0/zeit-data/          downloaded corpora, one folder per dataset
data for training/REFERENCE_REAL/
    events_impulse/    44 true impulsive events   <- THE REFERENCE
    events_clean/      28 clean-channel events
    events_all/        213 detected events
    analysis/          per-event JSON + CSV, stats_*.json
    report_impulse.html
DATA/                                   per-shot folders from the range trip
```

## The rule that makes the whole thing work

Real recordings are **not** the training set. They are the reference the
synthetic generator is validated against. The DNN trains on generated audio,
which is effectively unlimited — the limit is compute, not recordings.

Synthetic must be measured with **the same `analyze.py`** that measured the real
data, and compared against the **holdout split only**. Anything else is circular.

## What we already proved

| Result | Where |
|---|---|
| RMS does not converge for α-stable noise; percentile and FLOM do | `experiments/p1_normalisation.*` |
| The 1–2 kHz band — the one carrying speech intelligibility — recovers slowest after an impulse (464 ms) | `metrics/irt_real.*` |
| Our 44 events are genuinely impulsive: kurtosis 18.5, crest factor 17.9 dB, A-duration 0.27 ms | `REFERENCE_REAL/analysis/stats_impulse.json` |
