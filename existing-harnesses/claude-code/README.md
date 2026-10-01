# Claude Code CLI

These independent exercises follow the [build-your-own labs](../../labs/)
using Claude Code's built-in agent loop. Begin with [setup](lab00-setup/).
Each lab carries its own non-secret Foundry configuration example; it does
not read files from another lab folder.

| Lab | Capability |
|---|---|
| [0](lab00-setup/) | Foundry setup and authentication |
| [1](lab01-baseline/) | Constrained baseline, not a bare model call |
| [2A](lab02-tool-loop/) | Built-in tool loop |
| [2B](lab02b-hooks/) | Scoped rules and hooks |
| [3](lab03-sessions/) | Session resume |
| [4](lab04-planning/) | Plan mode and execution |
| [5](lab05-file-memory/) | File context, scoped rules, and freshness |
| [6](lab06-approval/) | Permissions and human approval |
| [7](lab07-observability/) | Session usage and observable events |
| [8](lab08-skills-tools/) | Skills and MCP |
| [9](lab09-background-agents/) | Delegation and background agents |
| [10](lab10-compaction/) | Context compaction |
| [11](lab11-loops/) | Bounded manual validation |
| [12](lab12-graphs/) | Human-orchestrated routing |
| [13](lab13-capstone/) | Planner, generator, evaluator |
| [14](lab14-comparison/) | Honest comparison |

**Preflight for every lab:** Install Claude Code following the
[official instructions](https://docs.anthropic.com/en/docs/claude-code/setup).
Check `claude --version` and `claude --help`. Follow the
[Microsoft Foundry guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code?tabs=bash):
copy **that lab's** `foundry.env.example` to a private temporary file
outside the repository, set the resource name to your own Foundry resource,
and source it. Sign in with `az login` for supported Entra authentication
or provide `ANTHROPIC_FOUNDRY_API_KEY` securely from your secret manager;
do not set both. Use a Claude deployment supported by your resource and
select its deployment identifier in the CLI. Test authentication in Lab 0
before the others. The build-your-own labs remain Entra-only.

Use only synthetic data and an isolated disposable workspace. A plan
mode, read-only request, or rule in `.claude/rules/` is **not** a hard
isolation or authorization boundary. Do not expose real files, production
resources, or secrets to the agent. Interactive permission prompts and
external isolation are essential for write drills. Never commit keys or
tokens, capture them in transcripts, or share them in chat. Clear temporary
workspaces and credentials afterward. Live runs require learner-provided
credentials and may incur charges; no live Foundry run or comparable
scored result is asserted here. Mark unavailable metrics as unavailable.
