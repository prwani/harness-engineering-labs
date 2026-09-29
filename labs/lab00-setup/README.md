---
layout: default
title: "Lab 0 — Setup, dual API, and scorecard"
---

# Lab 0 — Setup, dual API, and the scorecard

Lab 0 establishes the reusable boundary between Foundry-hosted Claude Messages
and GPT Responses models. It also supplies an offline `ScriptedModel`, a
provider usage ledger, and the deterministic local store simulator used by
Labs 0–8.

## Concept

Every later lab measures a *harness* capability against a fixed, known target —
so before any agent behavior can be built, the substrate has to be stable:
one Entra-only identity path (no API keys, ever), one interface over two
different provider APIs, and one deterministic "world" (the store simulator)
to run tasks against and grade honestly. Lab 0 has no agent behavior yet; it
is the plumbing everything else stands on.

**Key ideas**
- **Two providers, one seam.** Claude's Messages API and GPT's Responses API
  shape tool calls differently (message-grouped vs. `call_id`-addressed).
  `ModelClient`'s two adapters normalize both into the same `Turn`/`ToolCall`
  shape so later labs never special-case the provider.
- **Entra-only, no secrets.** `.env` holds only endpoint/deployment/provider;
  every credential is acquired at runtime via `DefaultAzureCredential`.
- **A ledger, not a guess.** Usage/cost is recorded exactly as each provider
  reports it — this is what later labs' scorecards and cost comparisons rely on.
- **A deterministic world to test against.** The local store simulator gives
  every later lab a stable, offline-checkable environment instead of a live,
  flaky dependency.

## Added in this lab

- [`harness/models/adapters.py`](harness/models/adapters.py) defines `ModelClient`
  and `Turn`, with `MessagesAdapter`, `ResponsesAdapter`, and the offline
  `ScriptedModel`.
- [`harness/config.py`](harness/config.py) provides `HarnessConfig` and
  `foundry_token_provider()` for non-secret configuration and Entra identity.
- [`harness/ledger.py`](harness/ledger.py) records provider-reported usage with
  `Ledger`; [`common/store_sim/app.py`](common/store_sim/app.py) supplies the
  seeded local store and read endpoints.
- [`harness/cli/app.py`](harness/cli/app.py) introduces `whoami()`, `ping()`,
  and simulator commands; [`lab.json`](lab.json) declares snapshot capabilities.

## Learner steps

1. Create and activate a virtual environment, install the lab, configure a
   Foundry deployment in `.env`, and sign in with Azure CLI:

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

2. Open the interactive prompt, ask multiple questions, and leave the prompt:

   ```bash
   harness ask
   ```

   Enter a question at `You>`; each `Assistant>` response and its token counts
   remain visible above the next prompt. Enter `/exit` to return to your shell.
   You can also pass one question directly, such as
   `harness ask "What is 17 multiplied by 23?"`. Each turn is a fresh model
   call without tools or conversation history. `pytest checks/` remains the
   offline regression check; it does not replace this learner-facing Foundry call.

Start the simulator in a separate terminal before inspecting or resetting it:

```bash
harness sim start
harness sim status
```

## Commands

- `harness ask` opens a persistent question prompt; `harness ask "<question>"`
  sends one stateless question to the configured Foundry model.
- `harness whoami` verifies that an Entra token can be acquired.
- `harness ping --provider claude|gpt [--probe]` validates a configured
  deployment and writes the capability record when probed.
- `harness sim start`, `harness sim status`, and `harness sim reset` manage
  the local simulator.

The next snapshot will add the first bare model call.
