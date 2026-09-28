---
layout: default
title: "Lab 11 — Loop engineering"
---

# Lab 11 — Loop engineering

This self-contained snapshot starts from Lab 10 and introduces a first-cut,
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

- live retry and polling behavior

All live paths must use Entra credentials and must not add API-key configuration.
