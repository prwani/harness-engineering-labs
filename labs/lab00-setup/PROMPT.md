# Lab 0 — Setup, dual API, and scorecard

Build a Python CLI named `harness` that uses Entra ID—not API keys—to prepare
Claude Messages and GPT Responses calls on Microsoft Foundry. Keep provider
differences behind a canonical `ModelClient` contract. Include a deterministic
scripted client and a local Store Simulator so all offline checks are free.

Run `pytest checks/` before moving to Lab 1.
