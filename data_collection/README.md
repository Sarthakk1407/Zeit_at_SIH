# data_collection

Tooling for the real gunshot data collection. **Documentation lives in
[`../docs/`](../docs/).**

| Doc | For |
|---|---|
| [`../docs/README.md`](../docs/README.md) | Documentation index |
| [`../docs/01-system/workflow.md`](../docs/01-system/workflow.md) | The whole system — papers, gaps, architecture |
| [`../docs/02-data-collection/toolkit-reference.md`](../docs/02-data-collection/toolkit-reference.md) | Tool reference and the range-day quickstart |
| [`../docs/02-data-collection/details.md`](../docs/02-data-collection/details.md) | Technical handover — what is measured, how, and the algorithms |
| [`../docs/02-data-collection/what-we-measure.md`](../docs/02-data-collection/what-we-measure.md) | Every measured quantity, its unit, and what breaks without it |

All commands are run **from this directory**:

```bash
cd data_collection
python3 make_test_data.py --out testdata/ && python3 selftest.py testdata/
python3 session.py init --name S1 --out ../DATA --hours 3.5
python3 capture.py --device "MacBook" --sr 44100
python3 session.py status ../DATA
```

`selftest.py` must print **ALL CHECKS PASSED** before range day.
