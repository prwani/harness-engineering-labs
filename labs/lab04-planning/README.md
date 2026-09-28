---
layout: default
title: "Lab 4 — Planning and todos"
---

# Lab 4 — Planning and todos

This self-contained snapshot starts from Lab 3 and introduces a first-cut,
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

- Foundry catalog remediation

All live paths must use Entra credentials and must not add API-key configuration.
