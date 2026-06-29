# Development Scripts

Manual diagnostic and exploration scripts. Not part of the production runtime.

Run from the repository root with `PYTHONPATH=.` (or `$env:PYTHONPATH='.'` on PowerShell).

| Script | Purpose |
|--------|---------|
| `test_routing.py` | Assistant intent routing regression checks |
| `test_auth_rbac.py` | Auth/RBAC manual integration script (see also `tests/`) |
| `test_assistant_context.py` | Assistant context window tests |
| `test_all_features.py` | Broad feature smoke script |
| `test_batch_query.py` | Batch query diagnostics |
| `test_explanation_error.py` | Prediction explanation error cases |
| `check_lookups.py` | Asset lookup validation |

Prefer `py -m pytest tests/` for automated CI-style verification.
