# Lab 10 — Compaction and repository map

This self-contained snapshot starts from Lab 9 and introduces a first-cut,
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

- long-running Foundry context profile

All live paths must use Entra credentials and must not add API-key configuration.
