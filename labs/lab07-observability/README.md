# Lab 7 — Observability and prompt caching

This self-contained snapshot starts from Lab 6 and introduces a first-cut,
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

- Application Insights traces
- Foundry prompt cache probe

All live paths must use Entra credentials and must not add API-key configuration.
