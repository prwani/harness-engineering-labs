# GitHub Copilot CLI

These standalone exercises follow the build-your-own capability sequence
using Copilot CLI. Start at [setup](lab00-setup/). Each lab has its own
non-secret `provider.env.example`; no lab reads from another lab folder.

| Lab | Capability |
|---|---|
| [0](lab00-setup/) | Foundry BYOK or GitHub authentication |
| [1](lab01-baseline/) | Constrained baseline; not a bare call |
| [2A](lab02-tool-loop/) | Built-in tools and loop |
| [2B](lab02b-hooks/) | Scoped instruction rules versus enforced tool permissions |
| [3](lab03-sessions/) | Resume |
| [4](lab04-planning/) | Plan and execution |
| [5](lab05-file-memory/) | Files, scoped rules and freshness |
| [6](lab06-approval/) | Interactive approval and permission limits |
| [7](lab07-observability/) | JSONL events and usage |
| [8](lab08-skills-tools/) | Skills and MCP |
| [9](lab09-background-agents/) | Fleet delegation |
| [10](lab10-compaction/) | Interactive compaction |
| [11](lab11-loops/) | Bounded manual validation |
| [12](lab12-graphs/) | Human routing versus CLI workflow |
| [13](lab13-capstone/) | Separate planner, generator and evaluator runs |
| [14](lab14-comparison/) | Honest cross-harness comparison |

**Each lab's preflight:** install `@github/copilot` following the
[official CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli);
run `copilot --version` and `copilot help providers`. Create a private,
temporary `COPILOT_HOME` (`export COPILOT_HOME="$(mktemp -d)"`; `chmod 700
"$COPILOT_HOME"`). Copy the lab's `provider.env.example` to a private file
*outside this repository*, edit non-secret endpoint and model names, and
source it. In Foundry BYOK mode set either `COPILOT_PROVIDER_API_KEY` from
a secret manager or `COPILOT_PROVIDER_BEARER_TOKEN` from an approved
Entra flow if supported by your endpoint; never put a credential in a
file, command line, shell history or transcript. The CLI's `azure` provider
sends the API key as `api-key` and a bearer token as `Authorization`.
Alternatively omit BYOK variables and authenticate with GitHub using
`copilot login`; that tests Copilot-hosted models, **not Foundry**.

The CLI options below were inspected on `@github/copilot` 1.0.90.
Verify `copilot --help` on your version. Use interactive mode for approval
exercises; `-p` in noninteractive mode requires automatic tool approval
and is unsuitable for the authorization drills. Do **not** use
`--allow-all`, `--allow-all-tools`, `--allow-all-paths` or `--yolo`.
Permissions and instruction files are different: instructions influence
model behavior, while permission filters and external isolation enforce
boundaries. Read-only prompts are not a sandbox or confidentiality boundary.
Work only with synthetic data in disposable directories, inspect edits,
never allow access to real secrets or live resources, and remove the
temporary workspace and `COPILOT_HOME` after each lab. Live exercises
require learner credentials and may incur charges; no comparable scorer
or live Foundry test is provided here. Record missing metrics as unavailable.
