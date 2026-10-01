# Codex CLI

| Lab | Exercise | Codex capability |
|---|---|---|
| 0 | [Setup](lab00-setup/) | Foundry provider and auth |
| 1 | [Constrained baseline](lab01-baseline/) | Built-in loop (not a bare call) |
| 2A | [Tool loop](lab02-tool-loop/) | Built-in shell tool |
| 2B | [Hooks and policy](lab02b-hooks/) | Command rules and policy limits |
| 3 | [Sessions](lab03-sessions/) | Resume |
| 4 | [Planning](lab04-planning/) | Plan-then-execute |
| 5 | [File memory](lab05-file-memory/) | Files and session scope |
| 6 | [Approval](lab06-approval/) | Sandbox and human approval |
| 7 | [Observability](lab07-observability/) | JSON events and usage |
| 8 | [Skills and MCP](lab08-skills-tools/) | Skills and MCP registration |
| 9 | [Delegation](lab09-background-agents/) | Child agents |
| 10 | [Compaction](lab10-compaction/) | Built-in context management |
| 11 | [Loops](lab11-loops/) | Explicit bounded validation |
| 12 | [Graphs](lab12-graphs/) | Manual routing (no native graph claim) |
| 13 | [Capstone](lab13-capstone/) | Planner / generator / evaluator |
| 14 | [Comparison](lab14-comparison/) | Control and provenance |

The exercises use a separate `CODEX_HOME` and do not change your usual Codex
configuration. Use a Foundry GPT deployment that supports the Responses API.
Each lab can be run independently: use that lab's own configuration example
and workspace; never import or copy material from another lab folder.
Instructions were checked against Codex CLI 0.159.3. Recheck `codex --help`
and `codex exec --help` on your installed version. Live runs cost money and
require learner-provisioned credentials; no live Foundry assertions are made
by this repository.

**Common preflight for each lab:** Install Codex CLI; create a private
`CODEX_HOME` with `mktemp -d` and `chmod 700`; copy that lab's
`config.toml.example` to `$CODEX_HOME/config.toml` and set your deployment,
endpoint and API version. Set `AZURE_OPENAI_API_KEY` in the environment from
a freshly obtained Entra token if supported (see [setup](lab00-setup/)), or
from your own resource key via a secret manager. Never write either value to
a lab file, terminal transcript, or commit. For noninteractive runs use
`--sandbox read-only` unless a lab explicitly requires **disposable local**
writes. A read-only sandbox restricts writes; it does *not* disable tools,
network access, the model's built-in agent loop, or all connectors.

Use only synthetic data and disposable directories. Do not grant access to
real customer data, live Azure resources, or privileged credentials. After
each lab, remove the disposable workspace and `CODEX_HOME` and unset the
credential. Record unsupported metrics as **unavailable**, not zero.
