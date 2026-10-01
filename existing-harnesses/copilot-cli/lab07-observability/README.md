# Lab 7 — Observability and caching

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace create `service.txt` with a synthetic port.
Inspect `copilot help monitoring`. In interactive `copilot -C
"$workdir"` ask for the port twice in *fresh* sessions; use `/usage`
and `/context` to inspect reported usage. If you choose JSONL output,
inspect `copilot --output-format json --help` and keep the stream
private; do not run `-p` with blanket approval on a real repository.

Record exposed usage, actual tool invocations, latency and provider
details. Do not infer cache savings or provider-reported tokens from
model output. Copilot's monitoring and CLI JSON events are not
automatically the build-your-own OTel span tree, per-tool cost
allocation or Foundry tracing. Mark unexposed fields unavailable and
never publish prompts or tool results from logs.
