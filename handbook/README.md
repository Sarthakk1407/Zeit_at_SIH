# handbook/

Standalone explainers for PS 26052, written to be handed to an evaluator
outside the team. Each file is a **single self-contained HTML page** — no build
step, no bundler, no local server. Open it in a browser, or publish it.

| File | What it is |
|---|---|
| [`zeit-handbook.html`](zeit-handbook.html) | **The whole project in one page.** Written so that nobody has to read `docs/` to understand the system — architecture, capture rig, measurement engine, offline pipeline, evaluation, papers, competition. Ten numbered figures carry the architecture; technical terms are marked and explained on hover. |
| [`zeit-audit.html`](zeit-audit.html) | **The design review.** Thirteen ranked findings, each traced to a specific paper, document or reproduced result. |
| [`zeit-bench-3d.html`](zeit-bench-3d.html) | **Interactive 3D model of the whole prototype**, with **both lanes modelled**. Headset, UMC202HD, Raspberry Pi 5 and the communication unit, wired as they actually connect. The earcup is cut away so the driver, the error microphone and the Lane A module are visible. Fires a simulated shot, writes every event to a timestamped log, and shows a four-channel signal monitor. |

## The ten figures

The handbook's architecture is carried by diagrams rather than prose. If an
evaluator reads only four, they should be 1, 2, 3 and 4.

| # | Section | Shows |
|---|---|---|
| 1 | masthead | **The whole system on one page** — air, three microphones, two lanes, two outputs, and the voice path into Mic 2 that must not exist |
| 2 | 03 Lanes | **Lane A in full** — the FxLMS loop, the secondary path, and why it is "filtered-x" |
| 3 | 04 Architecture | **Why the crack arrives 42 ms before the blast** — the geometry above, the true-millisecond timeline below |
| 4 | 05 Blocks | **Lane B, eleven blocks** — the classifier fork, the two paths, the merge, and the vocoder that is not ours |
| 5 | 05 Blocks | **What the classifier decides** — kurtosis to class to γ and β |
| 6 | 06 Hardware | **The real recordings are the reference, not the training set** |
| 7 | 06 Hardware | **The capture chain** and the staggered-gain array |
| 8 | 08 Offline | **The offline pipeline** — five stages, one shipped file |
| 9 | 09 Evaluation | **Where the metrics are measured**, and where they should also be |
| 10 | 16 Build order | **What blocks what** — the build dependency graph, and which stage to start first |

## Design

All three share one neutral document theme: white ground, near-black text,
hairline rules, generous spacing, and the **system typeface** — no web fonts are
loaded at all. Colour is used only where it carries information: severity in the
audit, lane identity in the handbook and the 3D model, status in the tables.
Both light and dark appearance are defined from the same token set, and the
diagrams inherit those tokens rather than hard-coding colours.

To restyle every page at once, edit the `:root` block at the top of each file.

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

The same reasoning applies to the handbook's figures: they are **inline SVG**,
written by hand against the CSS theme tokens, so they scale, they re-colour with
the theme, and they are searchable text rather than pictures of text.

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

## The 3D model

### Layout

Everything sits on **one bench plane**. The communication unit lies flat rather
than standing upright, the power supply is set back behind the board, and the
headset stand is cut to the height of the head it carries. The surface is
divided into three marked zones — **CAPTURE**, **COMPUTE**, **SINK** — which are
exactly the three stages of Lane B. Lane A appears in none of them, because
Lane A never leaves the earcup.

World scale is **1 unit = 10 mm** and component dimensions follow datasheets —
the Pi 5 board is `8.5 × 5.6` units because it is 85 × 56 mm.

### Both lanes

| Control | Effect |
|---|---|
| **Both lanes** | Everything |
| **Lane A only** | Hides the interface, the board, the radio and the Lane B cabling; moves to the earcup cutaway. The monitor drops to Mic 2 and Mic 3 |
| **Lane B only** | Hides Mic 3, the driver and the Lane A loop entirely — which is the correction: Mic 3 belongs to Lane A alone |

The right earcup's outer shell and face are **sectioned through one quadrant**,
so the driver, Mic 3 and the Lane A module read without the exploded view.

### The simulation

One scenario: **a shooter at 30 m firing a supersonic round.** Every timing is
derived from that geometry and the speed of sound, not chosen for effect.

| t | Event |
|---|---|
| 0 ms | Trigger. The muzzle blast begins expanding at 343 m/s |
| 36.5 ms | The bullet reaches its closest approach and generates the shockwave — about 3 m away, not 30 |
| 45.2 ms | **Crack arrives** (36.5 ms of flight + 8.7 ms of sound over the last 3 m) |
| 87.5 ms | **Blast arrives** (30 m ÷ 343 m/s). The 42.3 ms gap is the only genuine look-ahead a headset has |
| +0.42 ms | **Lane A** emits anti-noise at the driver |
| +0.55 ms | Lane A converged — in-ear residual 18.4 dB below the reference |
| +0.58 ms | Mic 1 after Mic 2 — the two are 20 cm apart on one head |
| +25.3 ms | **Lane B** completes, and goes out through the vocoder |

Propagation **distances are compressed** so a 30 m stand-off and a 19 cm head fit
in one frame. The **timings are not**: each wavefront reaches the head at its true
physical moment. No trace is a measured result — neither lane has been built.

## Editing

Open the file, edit, reload. Both pages are assembled from parts.

**The handbook** — edit `src/`, then rebuild:

```bash
cat src/01-head.html src/02-body-a.html src/03-blocks.html src/04-capture.html src/05-measure.html src/06-offline.html src/07-eval-papers.html src/08-gaps-ps.html src/09-drdo-comp.html src/10-build-open.html src/11-terms-a.html src/12-terms-b.html src/12b-terms-c.html src/13-script.html > zeit-handbook.html
```

- **Hover terms** are generated at runtime from the `TERMS` object in
  `src/11-terms-a.html`, `src/12-terms-b.html` and `src/12b-terms-c.html`
  (181 entries). Add an entry and every occurrence of that word in the prose is
  marked automatically — the copy is never touched. Each entry is
  `["definition", "how it is used here"]`.
- The term walker **deliberately skips anything inside an `<svg>`**. An HTML
  `<span>` inside an SVG `<text>` is not an SVG element, so the browser renders
  nothing and the word silently disappears from the figure. Do not remove that
  guard in `src/13-script.html`.
- **Figures** are inline SVG on a `viewBox` roughly 1000 units wide, using the
  `svg.dg` classes defined in `src/01-head.html` (`.box`, `.band`, `.t`, `.s`,
  `.e`, `.el`, `.hd`, `.n`). Arrowheads come from the shared `<defs>` block near
  the top of that file — `url(#ar)`, `#arT`, `#arA`, `#arB`, `#arC`.

**The 3D page** — edit `src3d/`, then rebuild:

```bash
cat src3d/01-shell.html src3d/02-notes.html src3d/03-scene.html src3d/04-geometry.html src3d/05-sim.html src3d/06-loop.html > zeit-bench-3d.html
```

`01` is the page shell and stylesheet, `02` the prose below the viewport, `03`
the scene, lane groups and damped camera, `04` all geometry, `05` labels, part
data, the lane filter and the monitor, `06` the run loop. Files `03`–`06` are one
continuous `<script>`, so `03` must not close it and `06` must.

- **Geometry** is in `src3d/04`. Sensor positions are the `P_MIC1` / `P_MIC2` /
  `P_MIC3` / `P_SPK` / `P_DSPA` constants; move one and the labels, cabling,
  Lane A loop and simulation follow.
- **The earcup cutaway** is an arc `CylinderGeometry` for the shell and a partial
  `CircleGeometry` for the face. After `rotation.z`, the shell's angle maps to
  world `(Y = r·sinθ, Z = r·cosθ)`; after `rotation.y`, the face's maps to
  `(Y = r·sinθ, Z = −r·cosθ)`. That sign flip is why the two arcs start at
  different angles for the same opening — the comment in `04` says so.
- **Lane grouping** is in `src3d/03`: `gLaneA`, `gIface`, `gPi`, `gRadio`,
  `gCabA`, `gCabB`. The lane filter in `05` just sets `.visible` on those.
- **Simulation timings** are the `T_BULLET` / `T_CRACK` / `T_BLAST` constants in
  `src3d/05`, and the log is the `EVENTS` array beside them — `[time, kind, html]`.
- **Monitor traces** are the `speechAt` / `crackAt` / `blastAt` / `mic3At` /
  `outAt` functions in `src3d/05`. They are a physical simulation, not
  recordings, and the page says so.

## Publishing

Republishing the same file path keeps the same URL.

## Source of truth

These pages **summarise** `docs/`; they do not replace it. Where the two
disagree, `docs/` is authoritative and the handbook is stale. Findings numbered
`F1`–`F13` refer to `zeit-audit.html`.
