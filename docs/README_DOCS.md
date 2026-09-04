# Documentation index

| Doc | What it covers | Read it if you are |
|---|---|---|
| [`ORDER.md`](ORDER.md) | **Start here.** What happens first, what each stage produces, what blocks what — plus what is missing from the research | figuring out what to do next |
| [`PLACEMENT.md`](PLACEMENT.md) | **Where everything goes.** Each paper and technique mapped to its block — hardware, on-device, or offline | asking "where does this fit" |
| [`WORKFLOW.md`](WORKFLOW.md) | **The whole system.** Papers, gaps, architecture, hardware, dataset, model, training, evaluation, deployment, what is ours | joining the project, or writing the presentation |
| [`DETAILS.md`](DETAILS.md) | Real gunshot data collection — what is recorded, how, all algorithms | working on data collection |
| [`WHAT_WE_MEASURE.md`](WHAT_WE_MEASURE.md) | Every measured quantity, its unit, what breaks without it | deciding what to capture |
| [`README.md`](README.md) | Tool reference and range-day quickstart | running the toolkit |
| [`zeit_anc_project_plan.md`](zeit_anc_project_plan.md) | Earlier project plan | looking for history |
| [`range_field_checklist.md`](range_field_checklist.md) | Field checklist | going to the range |

Code: [`../data_collection/`](../data_collection/) — run every command from there.
Source papers: [`../our notes from research paper/`](../our%20notes%20from%20research%20paper/)

## Diagrams

| Image | Shows |
|---|---|
| [`diagrams/1_signal_path.png`](diagrams/1_signal_path.png) | The on-device signal chain, each block labelled with the paper it comes from |
| [`diagrams/2_where_everything_goes.png`](diagrams/2_where_everything_goes.png) | Hardware / on-device / off-device — what lands where |
| [`diagrams/3_the_order.png`](diagrams/3_the_order.png) | Stage dependencies, and the branch that needs no hardware |

Regenerate with `python3 diagrams/make_diagrams.py` from the `docs/` directory.
