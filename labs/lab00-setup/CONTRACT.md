# Lab 0 contract

- `.env` holds only endpoint, deployment, and provider configuration; no API-key
  setting is accepted.
- `MessagesAdapter` and `ResponsesAdapter` emit canonical `Turn` and
  `ToolCall` values.
- A GPT tool call uses `call_id` as the canonical ID and retains its item ID
  separately.
- Usage is recorded exactly as supplied by each provider.
- `harness ping --probe` writes `runs/capabilities.json`.
- `harness sim status` displays deterministic seeded products.
