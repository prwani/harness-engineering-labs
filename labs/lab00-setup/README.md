# Lab 0 — Setup, dual API, and the scorecard

Lab 0 establishes the reusable boundary between Foundry-hosted Claude Messages
and GPT Responses models. It also supplies an offline `ScriptedModel`, a
provider usage ledger, and the deterministic local store simulator used by
Labs 0–8.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
az login
pytest checks/
```

Set only non-secret values in `.env`. Authentication is acquired at runtime
through `DefaultAzureCredential`; do not add API keys.

Start the simulator in a separate terminal before inspecting or resetting it:

```bash
harness sim start
harness sim status
```

## Commands

- `harness whoami` verifies that an Entra token can be acquired.
- `harness ping --provider claude|gpt [--probe]` validates a configured
  deployment and writes the capability record when probed.
- `harness sim start`, `harness sim status`, and `harness sim reset` manage
  the local simulator.

The next snapshot will add the first bare model call.
