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
| [`problem-statement.txt`](03-source-material/problem-statement.txt) | PS 26052 in full |
| [`project-plan-v0.md`](03-source-material/project-plan-v0.md) | The earlier project plan, kept for history |

Research papers and notes: [`../our notes from research paper/`](../our%20notes%20from%20research%20paper/)

## diagrams

| Image | Shows |
|---|---|
| [`1_signal_path.png`](diagrams/1_signal_path.png) | The on-device chain, each block labelled with its source paper |
| [`2_where_everything_goes.png`](diagrams/2_where_everything_goes.png) | Hardware / on-device / offline — what lands where |
| [`3_the_order.png`](diagrams/3_the_order.png) | Stage dependencies, and the branch needing no hardware |

Regenerate: `python3 diagrams/make_diagrams.py` from this directory.

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
