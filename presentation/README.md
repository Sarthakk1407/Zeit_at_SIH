# presentation/

The SIH 2026 idea submission deck, built on the official template.

| File | What it is |
|---|---|
| `ZEIT_SIH2026_Idea.pptx` | **The deliverable.** Six slides, on the official template. |
| `template.pptx` | The unmodified `SIH2026-IDEA-Presentation-Format.pptx` as supplied. |
| `build_deck.py` | Generates the deck from the template. |
| `deckkit.py` | Drawing primitives — chips, arrows, stat callouts — plus a text-fit checker. |
| `qa_geometry.py` | Geometric QA: safe area, chrome collisions, overlaps, overflow. |
| `render_preview.py` | Renders each slide to `preview/slide-N.png` for visual inspection. |
| `mentor-approval.png` | The mentor's approval email, as captured. |
| `mentor-approval-crop.png` | Generated — the same image cropped to the email body. Do not edit; it is rebuilt each run. |

## Rebuild

```bash
python build_deck.py && python qa_geometry.py && python render_preview.py
```

All three must come back clean: no text-fit warnings, `problems: 0`, six PNGs.

## Constraints taken from the template

The template's own instruction slide sets the rules, and the build honours all
of them:

- **Six slides maximum, including the title slide.** The instruction slide is
  removed — the template says it may be — and its part is dropped from the
  package, not merely unlinked.
- **The idea-detail pointers must not be changed.** Every pointer is read out of
  the template at build time and re-emitted **verbatim**, repositioned as a
  section label rather than deleted. `qa_geometry.py` will not catch a dropped
  pointer, so the check is in the build: if a pointer index moves, the slide
  fails loudly rather than silently losing it.
- **Points, diagrams and infographics rather than paragraphs.** Every slide is
  built from flow chips, arrows and callouts; there is no body-copy block
  anywhere in the deck.

## Slides

| # | Section | Principal visual |
|---|---|---|
| 1 | Title page | Problem statement identity, team, one-line positioning |
| 2 | Idea title / proposed solution | **Two-lane architecture flow** — Lane A protection against Lane B transmit, requirement→mechanism mapping, five numbered differentiators |
| 3 | Technical approach | **Three stacked flowcharts** — hardware chain, the eleven-block Lane B chain with the two-path branch, and the offline pipeline; latency budget beneath |
| 4 | Feasibility and viability | Four evidence callouts, three feasibility proofs, five risk→strategy pairs |
| 5 | Impact and benefits | Three audience cards, four benefit cards, target-metric strip |
| 6 | Research and references | Sixteen sources in four grouped columns, four "where the published work stops" cards |

## A note on QA

LibreOffice is not installed in this environment, so the usual
`soffice --convert-to pdf` route for visual QA is unavailable. Two substitutes
are used instead, and both are stricter than eyeballing a render:

- `deckkit.check_fit()` measures every string against the **real Arial metrics**
  from `C:/Windows/Fonts` and reports anything that cannot fit the width it was
  given.
- `qa_geometry.py` computes every shape's bounding box and reports content
  outside the safe area, collisions with the template's logo, footer bar and
  team badge, overlapping text boxes, and text wider than its container.
- `render_preview.py` then draws the slides from the shape tree so the layout
  can actually be looked at.

The previews are an approximation of PowerPoint's renderer — arrows draw as
rounded blocks and theme-filled template shapes are omitted — so treat them as a
layout check, not a colour proof.

## The mentor approval image

`build_deck.py` looks for `mentor-approval.png` (hyphen, underscore or space all
work), crops it to the email body — the raw capture is a whole browser window and
the Gmail chrome is unreadable at slide scale — and places it on slide 2. Replace
the source file and rebuild; the crop and placement follow automatically. If the
file is missing, a quoted-text block is used instead, so the build never breaks.

## Before uploading

1. Open in PowerPoint and fill **Team ID** on slide 1 (currently `(from SIH
   portal)`).
2. Team name is `ZEIT v.1.0`, set by `TEAM` at the top of `build_deck.py`.
   It appears once, on the title slide — the template's per-slide team badge is
   deliberately removed from slides 2–6.
3. **Export to PDF.** The portal accepts PDF only; no PPT, DOC or other format
   is supported. Exporting from PowerPoint rather than a converter keeps the
   Arial metrics the layout was measured against.
