# handbook/

The evaluator-facing pages for **ANVIL** (Adaptive Noise Void with Intelligent
Lanes), Team ZEIT's entry for Smart India Hackathon 2026, PS 26052. This folder
is the site root of the deployment at
[zeit-handbook.netlify.app](https://zeit-handbook.netlify.app).

| Page | What it is |
|---|---|
| [`index.html`](index.html) | **The System Handbook.** The whole project on one page: the problem, the two lanes, the headset, both signal chains, training, the measured proof, one gunshot traced through both lanes, how each clause of the problem statement is met, fail-safe behaviour and cost. |
| [`zeit-bench-3d.html`](zeit-bench-3d.html) | **The prototype bench in 3D, with both lanes running.** Every part at its datasheet size, the signal spine wired between them, the earcup opens on a click, and underneath Lane A and Lane B run as real DSP code at 16 kHz with a four-trace scope, sound-pressure meters and the Jetson to STM32 firmware link. "Fire a shot" traces one gunshot through both lanes in slow motion. |
| [`zeit-audit.html`](zeit-audit.html) | **The design review.** The team's audit of its own first design: thirteen findings, each traced to a paper, a document or a reproduced result, with what the locked architecture did about every one and where to check it. |

## The proof is real output

The terminal panels in the handbook are not typed. Each one is the saved output of
a real run, kept in [`proof/`](proof/) and inserted by the build as it stands.

| File | Command | Shows |
|---|---|---|
| `proof/training-selftest.txt` | `training/` · `python selftest.py` | The voice-lane pipeline end to end, 13 of 13 checks |
| `proof/latency-benchmark.txt` | `training/` · `python bench_latency.py` | The three-input network timed frame by frame, with export parity |
| `proof/capture-validate.txt` | `data_collection/` · `python validate.py good_shots.wav --expect-events 5` | The range-day verdict on one take |
| `proof/capture-selftest.txt` | `data_collection/` · `python selftest.py testdata/` | The capture toolkit checking itself |
| `proof/normalisation.txt` | `synthetic_generator/experiments/` · `python p1_normalisation.py` | Why RMS does not converge on impulsive noise |
| `proof/gunshot-run.txt` | `handbook/proof/` · `node gunshot_run.mjs` | The 3D bench's gunshot run, computed without a browser |

The recovery-time chart is drawn from `synthetic_generator/metrics/irt_real.json`,
the recorded result of `irt.py` on the team's own range recordings.

## Building

```
python build_handbook.py                              # src/*.html + proof/ -> index.html, zeit-audit.html
cat src3d/0*.html > zeit-bench-3d.html                # the 3D bench, from its ten source parts
```

To refresh a terminal panel, re-run its command, save the output over the file in
`proof/`, and build again. `build_handbook.py` lists every command at its top.

## Layout

```
handbook/
  index.html            built: the System Handbook
  zeit-bench-3d.html    built: the 3D bench
  zeit-audit.html       built: the design review
  build_handbook.py     builds both pages
  src/handbook.html     the handbook's template (its style is shared with the review)
  src/audit.html        the design review's template
  src3d/01 ... 09       the 3D bench's source, in order
  proof/                saved terminal output, and the headless gunshot runner
  img/                  the three images the handbook uses (our own renders and range photographs)
```

## Design

The handbook is one page with no script and no web font. It loads three images
from `img/` and nothing else. Colour carries meaning throughout: green is the ear
lane, blue the voice lane, red impulse handling, orange adaptation, purple the
neural network. Light and dark appearance come from the same token set at the top
of `src/handbook.html`.

The 3D bench loads `three.js` 0.169 as ES modules from jsDelivr, with
`OrbitControls`, `RoomEnvironment` and `RoundedBoxGeometry`. The headset and every
board are built in code from the dimensions in
[`../synthetic_generator/HARDWARE.md`](../synthetic_generator/HARDWARE.md), so no
third-party model file is carried. The DSP, the FFT, the scope and the meters are
written in the page; no audio library is loaded and nothing is recorded or played.

### What the bench simulates

Signals are synthetic and are carried in pascals, so every level on the panel is a
real sound-pressure figure for the signal being computed. Lane A runs sample by
sample: clip flag, hear-through band, level-dependent gain, crack guard, limiters
and a 32-tap filtered-x LMS canceller with a secondary-path model. Lane B runs
once per 16 ms frame: impulse detector, robust (90th-percentile) level
normalisation, STFT, a Wiener mask standing in for the trained network, the
throat-microphone voice guard, the scene classifier and the firmware link. The
trained GTCRN network itself runs on the Jetson through TensorRT; it cannot run in
a browser.

`window.ZEIT` exposes the scene, the parts, the simulation (`ZEIT.SIM`) and
`ZEIT.fireShot()` for testing from the console.
