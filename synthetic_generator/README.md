# synthetic_generator

Everything needed to build the dataset pipeline and the ML model, in four files.

| File | What it answers |
|---|---|
| **`DATASET_SPEC.md`** | *What audio do we need and where does it come from?* — 20 noise classes, every corpus, clean speech, RIRs, HRTFs, target sizes, licences |
| **`MODEL_VALUES.md`** | *What numbers does the model need?* — STFT/ERB settings, architecture, training hyperparameters, SNR range, augmentation, evaluation targets, edge deployment, and the measured real reference |
| **`PHASES.md`** | *What order does it happen in?* — Phases 0–7 with dependencies and status |
| **`CHECKLIST.md`** | *What is done and what is left?* — tick as you go |

## Where the real data lives

```
REFERENCE_REAL/
  events_impulse/   44 true impulsive events  ← the reference
  events_clean/     28 clean-channel events
  events_all/       213 detected events
  analysis/         per-event JSON+CSV, stats_*.json
  report_impulse.html
DATA/               per-shot folders (raw, events, analysis, quicklook, validate)
VALIDATION_SET/     8 clean takes
```

## The rule that makes the whole thing work

Real recordings are **not** the training set. They are the reference the
synthetic generator is validated against. The DNN trains on generated audio,
which is effectively unlimited — the limit is compute, not recordings.

Synthetic must be measured with **the same `analyze.py`** that measured the
real data, and compared against the **holdout split only**.

## Right now, the two things that unblock the most

1. **Decide the clean speech corpus** (Phase 0d) — a decision, not work. It
   blocks Phase 4 entirely.
2. **Download NOISEX-92** — the only corpus with actual tank, military aircraft
   and machine-gun recordings.
