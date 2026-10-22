# FuGu test report

Date: 22 October 2026

## Executed checks

- `python -m py_compile app.py fugu_logic.py test_fugu_logic.py` — passed.
- `python -m unittest -v test_fugu_logic.py` — 7 tests passed.
- JSON dataset structural checks performed by the unit tests — passed for IDs, required fields and HTTPS format.

## Not executed

The Streamlit package is not installed in the creation environment. An attempt to run `python -m pip install -r requirements.txt` failed because package-index DNS/network access was unavailable. Therefore, **the browser UI has not been launched or end-to-end tested in this environment**. Run it locally using the steps in `README.md` and repeat the manual-test checklist before publishing.

## What the tests do not establish

Passing unit tests verifies selected deterministic functions only. It does not prove every Streamlit interaction works in a real browser, nor does it independently verify the live accuracy/completeness of all external university pages. Links and facts should be reviewed again before use in a research report.
