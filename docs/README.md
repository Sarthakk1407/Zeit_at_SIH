# ZEIT — documentation

SIH 2026, PS 26052 (DRDO) — AI/ML adaptive noise cancellation for defence.

## Start here

| # | Read | If you are |
|---|---|---|
| 1 | [What we are building](01-system/workflow.md) | new to the project |
| 2 | [Where everything goes](01-system/placement.md) | asking "where does this paper fit" |
| 3 | [The order](01-system/order.md) | asking "what do I do next" |

## 01-system — the design

| Doc | Covers |
|---|---|
| [`workflow.md`](01-system/workflow.md) | **The whole system.** All 16 sources, every gap we build on, architecture, hardware, dataset, model, training, evaluation, deployment, what is genuinely ours |
| [`placement.md`](01-system/placement.md) | **Where everything goes.** Each paper mapped to its block — hardware, on-device, or offline. Which five sources actually ship code |
| [`two-mic-capture-plan.md`](01-system/two-mic-capture-plan.md) | **The capture plan.** Two mics — one at the gun, one at the speaker. Take types, the look-ahead the geometry buys, and what must be verified before range day |
| [`architecture.md`](01-system/architecture.md) | **The final, locked architecture — authoritative.** Lane A (ADAU1787 + STM32: hear-through, crack guard, 82 dB limiter, ANC in both ears, automatic modes) and Lane B (Jetson Orin Nano Super: 3-input GTCRN with TensorRT, radio receive cleaning). The 6-mic headset, every step, timing, failure behaviour, proven vs designed, gates |
| `ZEIT_Architecture.docx` / `.pdf`, `ZEIT_Hardware.docx` / `.pdf` (in `01-system/`) | Printable copies of the architecture and the hardware, sharing step and hardware IDs, each with 5 blank revision pages |
| [`tech-stack.md`](01-system/tech-stack.md) | **The stack.** SigmaStudio + STM32 C for Lane A, TensorRT + C++ on the Jetson for Lane B, PyTorch offline; the locked audio settings and the parity test |
| [`compatibility-audit.md`](01-system/compatibility-audit.md) | **The audit.** Every hardware and software link with status (VERIFIED / TESTED / CALCULATED / UNKNOWN), the 12 problems found and fixed, and the staged buy-and-test plan |
| [`order.md`](01-system/order.md) | **The sequence.** What each stage produces, what blocks what — plus what is missing from the research |

## 02-data-collection — the real gunshot data

| Doc | Covers |
|---|---|
| [`details.md`](02-data-collection/details.md) | Technical handover — what is recorded, how, and every algorithm |
| [`what-we-measure.md`](02-data-collection/what-we-measure.md) | All 16 measured quantities, units, and what breaks without each |
| [`toolkit-reference.md`](02-data-collection/toolkit-reference.md) | Tool reference and the range-day quickstart |
| [`field-checklist.md`](02-data-collection/field-checklist.md) | Printable field checklist |
| [`metadata-template.csv`](02-data-collection/metadata-template.csv) | Metadata schema |

## 03-source-material

| Doc | Covers |
|---|---|
| [`ps-26052.md`](03-source-material/ps-26052.md) | **PS 26052 in full** — title, background, description, expected solution, verbatim |
| [`problem-statement.txt`](03-source-material/problem-statement.txt) | Despite the name, a pasted planning chat (range toolkit prompt), not the PS |
| [`project-plan-v0.md`](03-source-material/project-plan-v0.md) | The earlier project plan, kept for history |

## research — the sources

| Folder | Holds |
|---|---|
| [`research/`](research/) | The papers themselves, converted to Markdown (Widrow, NOISEX-92, BMRI, Deep ANC, dual-mic DC-CRN, GTCRN, H-GTCRN, DeepFilterNet2, α-stable, IS³, SDR, DNSMOS …) |
| [`research-summary/`](research-summary/) | The team's reading notes and gap analysis (`PS26052_paper_gap_analysis.docx` and friends) that `workflow.md` is built on |

## Beyond `docs/`

| Folder | What it is |
|---|---|
| [`../synthetic_generator/`](../synthetic_generator/) | **The dataset pipeline and current status.** Downloaded corpora (11 datasets, ~229k files), the real reference (44 impulsive events from the 7 Sep 2026 range trip), the phase plan and checklist, IRT / WLPS metrics and the normalisation experiment. Its `PHASES.md` and `CHECKLIST.md` are the live progress tracker; the stage statuses in `order.md` are the original plan |
| [`../handbook/`](../handbook/) | The evaluator-facing pages, below |
| `../presentation/` | The SIH idea-submission deck, built by script from the official template (not tracked in git) |

## diagrams

| Image | Shows |
|---|---|
| [`1_signal_path.png`](diagrams/1_signal_path.png) | The on-device chain, each block labelled with its source paper |
| [`2_where_everything_goes.png`](diagrams/2_where_everything_goes.png) | Hardware / on-device / offline — what lands where |
| [`3_the_order.png`](diagrams/3_the_order.png) | Stage dependencies, and the branch needing no hardware |
| [`4_architecture_full.png`](diagrams/4_architecture_full.png) | **The big one.** Headset with 3 mics, the whole on-device chain, the offline side, and why there are two paths |
| [`5_signal_path_detail.png`](diagrams/5_signal_path_detail.png) | Every block: what it does, which algorithm, why it is there |
| [`6_tech_stack.png`](diagrams/6_tech_stack.png) | C++ / hand-written / Python, and the ONNX boundary |

Regenerate: `python3 diagrams/make_diagrams.py` and
`python3 diagrams/make_arch_diagrams.py` from this directory.

> ⚠️ Diagrams 1, 4, 5 and 6 still show the **earlier** design (3-mic headset,
> Raspberry Pi, Aux-IVA, 20 ms frames). They are no longer embedded in the
> system documents; the text diagrams in `architecture.md` are current.

## The evaluator-facing pages

Single self-contained HTML files in [`../handbook/`](../handbook/), written to be
handed to someone outside the team. They summarise these documents; where the two
disagree, `docs/` is authoritative.

| Page | What it is |
|---|---|
| [`index.html`](../handbook/index.html) | **The whole project in one page** (live at <https://zeit-handbook.netlify.app/>), with ten figures carrying the architecture and hover definitions on every technical term |
| [`zeit-bench-3d.html`](../handbook/zeit-bench-3d.html) | **The prototype bench in 3D, with both lanes running** (live at <https://zeit-handbook.netlify.app/zeit-bench-3d>). Every part at its datasheet size, the signal spine wired, the earcup opens on a click — and a live 16 kHz simulation underneath: hear-through, crack guard, limiters and a filtered-x LMS canceller for Lane A; framing, STFT, Wiener mask and voice guard for Lane B; the scene classifier and the Jetson↔STM32 message log, laid out as a document with instrument panels rather than a full-screen scene. **Fire a shot** traces one gunshot at 30 m through both lanes in slow motion, with every figure in its log measured from the same engine (crack guard 0.01 ms after the crack, hear-through down 42 ms before the blast, peak at the ear 112.8 dBP, IRT by the irt.py definition). Sources in `handbook/src3d/`, built with `cat src3d/0*.html > zeit-bench-3d.html` |
| [`zeit-audit.html`](../handbook/zeit-audit.html) | **The design review** — thirteen ranked findings, each traced to a source |
| [`zeit-handbook-new.html`](../handbook/zeit-handbook-new.html) | **The final architecture as a readable handbook** — both lanes step by step, the 6-mic headset, hardware, compatibility, feasibility (internal reading copy, not deployed) |

The deployed `index.html` and the 3D model were written for the earlier
Raspberry Pi design; each carries a notice pointing to the final architecture.

## Code

[`../data_collection/`](../data_collection/) — 16 CLI tools. Run every command
from that directory.

```bash
cd data_collection
python3 make_test_data.py --out testdata/ && python3 selftest.py testdata/
python3 session.py init --name S1 --out ../DATA --hours 3.5
python3 capture.py --device "USB2.0" --sr 48000
python3 session.py status ../DATA
```
