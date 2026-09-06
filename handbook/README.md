# handbook/

Standalone explainers for PS 26052, written to be shared outside the team.
Each file is a **single self-contained HTML page** — no build step, no bundler,
no local server. Open it in a browser, or publish it.

| File | What it is |
|---|---|
| [`zeit-handbook.html`](zeit-handbook.html) | **The whole project in one page.** Written so that nobody has to read `docs/` to understand the system — architecture, capture rig, measurement engine, offline pipeline, evaluation, papers, competition. Technical terms are marked and explained on hover. |
| [`zeit-audit.html`](zeit-audit.html) | **The design review.** Thirteen ranked findings, each traced to a specific paper, document or reproduced result. |
| [`zeit-bench-3d.html`](zeit-bench-3d.html) | **Interactive 3D model of the whole prototype** — headset, Behringer UMC202HD and Raspberry Pi 5 with its cooler, supply and card, wired as they actually connect. Fires a simulated shot, writes every event to a timestamped log that stays on screen, and shows a three-channel signal monitor. |

## Design

All three share one neutral document theme: white ground, near-black text,
hairline rules, generous spacing, and the **system typeface** — no web fonts are
loaded at all. Colour is used only where it carries information: severity in the
audit, sensor identity in the 3D model, status in the tables. Both light and dark
appearance are defined from the same token set.

To restyle every page at once, edit the `:root` block at the top of each file, or
re-run `src/restyle_audit.py` after changing the theme in that script.

## Why single files

These pages are published as Artifacts, which are served under a strict content
security policy:

- Scripts load **only** from `cdnjs.cloudflare.com`, `cdn.jsdelivr.net/npm`,
  `cdn.tailwindcss.com` and `code.jquery.com`.
- **Every other external fetch is blocked** — images, media, `fetch`/XHR, and any
  3D asset file (`.gltf`, `.glb`, `.obj`, `.fbx`).

That last point is why the headset is **built procedurally in code** rather than
loaded from a downloaded model. It is also the better engineering choice: the
geometry follows the dimensions in
[`../docs/01-system/architecture.md`](../docs/01-system/architecture.md), so the
distances on screen are the distances in the specification rather than an
artist's approximation — and there is no third-party asset licence to carry into
a DRDO deliverable.

## Dependencies

| Page | Loads |
|---|---|
| `zeit-handbook.html` | Nothing |
| `zeit-audit.html` | Nothing |
| `zeit-bench-3d.html` | `three.js` r128 (UMD, global `THREE`) from cdnjs |

Camera orbit, panning, pinch-zoom, label projection and picking are all
hand-written — `OrbitControls` and `CSS2DRenderer` ship as ES modules the UMD
build does not include, so depending on them would have added a second loading
path for about sixty lines of code.

## The simulation

The 3D page plays one scenario: **a shooter at 30 m firing a supersonic round.**
Every timing is derived from that geometry and the speed of sound, not chosen for
effect.

| t | Event |
|---|---|
| 0 ms | Trigger. The muzzle blast begins expanding at 343 m/s |
| 36.5 ms | The bullet reaches its closest approach and generates the shockwave — about 3 m away, not 30 |
| 45.2 ms | **Crack arrives** (36.5 ms of flight + 8.7 ms of sound over the last 3 m) |
| 87.5 ms | **Blast arrives** (30 m ÷ 343 m/s). The 42.3 ms gap is the only genuine look-ahead a headset has |
| +0.58 ms | Mic 1 after Mic 2 — the two are 20 cm apart on one head |
| +25.3 ms | Lane B completes. Lane A responded within 1 ms |

Propagation **distances are compressed** so a 30 m stand-off and a 19 cm head fit
in one frame. The **timings are not**: each wavefront reaches the head at its true
physical moment.

## Editing

Open the file, edit, reload.

- **The handbook is assembled from `src/`.** Edit the parts, then rebuild:
  ```bash
  cat src/01-head.html src/02-body-a.html src/03-blocks.html src/04-capture.html \
      src/05-measure.html src/06-offline.html src/07-eval-papers.html \
      src/08-gaps-ps.html src/09-drdo-comp.html src/10-build-open.html \
      src/11-terms-a.html src/12-terms-b.html src/12b-terms-c.html \n      src/13-script.html > zeit-handbook.html
  ```
- **Hover terms** are generated at runtime from the `TERMS` object in
  `src/11-terms-a.html`, `src/12-terms-b.html` and `src/12b-terms-c.html` (181 entries). Add an entry and every
  occurrence of that word in the prose is marked automatically — the copy is
  never touched. Each entry is `["definition", "how it is used here"]`.
- **The 3D page is assembled from `src3d/`.** Same pattern:
  ```bash
  cat src3d/01-shell.html src3d/02-notes.html src3d/03-scene.html \n      src3d/04-geometry.html src3d/05-sim.html src3d/06-loop.html > zeit-bench-3d.html
  ```
  `01` is the page shell and stylesheet, `02` the prose below the viewport, `03`
  the scene and damped camera, `04` all geometry, `05` labels/part data/monitor,
  `06` the run loop. Files `03`–`06` are one continuous `<script>`, so `03` must
  not close it and `06` must.
- **Geometry** is in `src3d/04`. World scale is **1 unit = 10 mm** and component
  dimensions follow datasheets — the Pi 5 board is `8.5 × 5.6` units because it
  is 85 × 56 mm. Sensor positions are the `P_MIC1` / `P_MIC2` / `P_MIC3` /
  `P_SPK` constants; move one and the labels, cabling and simulation follow.
- **Simulation timings** are the `T_BULLET` / `T_CRACK` / `T_BLAST` constants in
  `src3d/05`, and the log is the `EVENTS` array beside them — `[time, kind, html]`.
- **Monitor traces** are the `speechAt` / `crackAt` / `blastAt` / `outAt`
  functions in `src3d/05`. They are a physical simulation, not recordings, and
  the page says so.

## Publishing

Republishing the same file path keeps the same URL.

## Source of truth

These pages **summarise** `docs/`; they do not replace it. Where the two
disagree, `docs/` is authoritative and the handbook is stale. Findings numbered
`F1`–`F13` refer to `zeit-audit.html`.
