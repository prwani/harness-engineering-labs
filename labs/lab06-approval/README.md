# Lab 6 — Tool approval and safety gates

This self-contained snapshot starts from Lab 5 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Offline verification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest checks/
harness lab-info
```

## Live validation (not run locally)

The following integrations require learner-provisioned credentials and resources:

- human approval flow

All live paths must use Entra credentials and must not add API-key configuration.
