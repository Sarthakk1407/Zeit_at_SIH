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
| [`workflow.md`](01-system/workflow.md) | **The whole system.** All 14 sources, every gap we build on, architecture, hardware, dataset, model, training, evaluation, deployment, what is genuinely ours |
| [`placement.md`](01-system/placement.md) | **Where everything goes.** Each paper mapped to its block — hardware, on-device, or offline. Which five sources actually ship code |
| [`two-mic-capture-plan.md`](01-system/two-mic-capture-plan.md) | **The capture plan.** Two mics — one at the gun, one at the speaker. Take types, the look-ahead the geometry buys, and what must be verified before range day |
| [`architecture.md`](01-system/architecture.md) | **The product's software architecture.** Organised around the two lanes: Lane A, the sub-millisecond FxLMS hearing-protection loop, and Lane B, the 11-block speech engine. The 3-mic headset, every algorithm in plain language, the timing budget, and the innovations |
| [`tech-stack.md`](01-system/tech-stack.md) | **The stack.** C++ for the real-time path, Python for ML, the latency budget that fixes every other decision, and the parity test that keeps them honest |
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

## The evaluator-facing pages

Single self-contained HTML files in [`../handbook/`](../handbook/), written to be
handed to someone outside the team. They summarise these documents; where the two
disagree, `docs/` is authoritative.

| Page | What it is |
|---|---|
| [`index.html`](../handbook/index.html) | **The whole project in one page** (live at <https://zeit-handbook.netlify.app/>), with ten figures carrying the architecture and hover definitions on every technical term |
| [`zeit-bench-3d.html`](../handbook/zeit-bench-3d.html) | **Interactive 3D model of the prototype** (live at <https://zeit-handbook.netlify.app/zeit-bench-3d>), both lanes modelled, earcup cut away, with a lane filter and a simulated shot |
| [`zeit-audit.html`](../handbook/zeit-audit.html) | **The design review** — thirteen ranked findings, each traced to a source |

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
