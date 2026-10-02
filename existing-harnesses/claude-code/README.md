# Claude Code CLI

These exercises follow the [build-your-own labs](../../labs/) capability
sequence, using Claude Code's built-in agent loop instead of writing one.
Rather than a toy prompt per lab, you build **one small Python app** (a
synthetic pet-store order calculator) in Lab 2A and keep extending it.
Each later lab adds one harness capability to the same codebase, so you
see what the harness adds to real work rather than to a quiz question.

| Lab | Capability | What you do to the app |
|---|---|---|
| [0](lab00-setup/) | Foundry setup and authentication | Create `app/` as a git repo; verify a live call |
| [1](lab01-baseline/) | Constrained baseline vs agent | Same question with tools off and on |
| [2A](lab02-tool-loop/) | Built-in tool loop (files, shell, git, tests) | Build the app; find a regression with git history |
| [2B](lab02b-hooks/) | Scoped rules and hooks | Rule for money math; hooks that block edits and auto-run tests |
| [3](lab03-sessions/) | Sessions: continue, resume, fork | Pause work, change the repo outside Claude, resume, fork |
| [4](lab04-planning/) | Plan mode | Plan, critique and then execute a discount-codes feature |
| [5](lab05-file-memory/) | Project memory (`CLAUDE.md`) and freshness | `/init`, team conventions, edit memory mid-session |
| [6](lab06-approval/) | Permissions and approval | Allow/ask/deny rules vs a fake secret and a prompt injection |
| [7](lab07-observability/) | Observability | Headless JSON event stream, cost, context, transcripts, OTel |
| [8](lab08-skills-tools/) | Skills and MCP | `release-notes` skill; a local synthetic orders MCP server |
| [9](lab09-background-agents/) | Subagents and background agents | Parallel security review + test writing; `--bg` sessions |
| [10](lab10-compaction/) | Context compaction | 6,000-line log, `/context`, focused `/compact`, fact check |
| [11](lab11-loops/) | Bounded loops | Prompted loop vs a deterministic Stop-hook gate; budget caps |
| [12](lab12-graphs/) | Human-orchestrated routing graph | Classifier routes tickets to tool-scoped specialist calls |
| [13](lab13-capstone/) | Planner, generator, evaluator | Scripted PGE loop with an independent evaluator |
| [14](lab14-comparison/) | Honest comparison | Same task across Claude Code, Codex and your own harness |

## Prerequisites

- Claude Code and the Foundry env script from [Lab 0](lab00-setup/)
  (done **once**; every later lab reuses it).
- `git` (on Windows, install [Git for Windows](https://git-scm.com/download/win);
  Claude Code then uses its Bash tool) with `user.name` and `user.email`
  configured.
- Python 3.10+ with `pytest` (`python -m pip install pytest`). On
  macOS/Linux, if only `python3` exists, replace `"command": "python"` with
  `"command": "python3"` in the copied `.claude/settings.json` files.
- PowerShell 7+ on Windows (the Lab 12/13 scripts pass JSON arguments that
  Windows PowerShell 5.1 mangles).

## Working in `app/`

```text
existing-harnesses/claude-code/
├── claude-code.env.ps1 / .sh   # Lab 0, gitignored: Foundry settings
├── .azure-cli/                 # Lab 0, gitignored: scoped az login
├── app/                        # Lab 0, gitignored: YOUR practice app (own git repo)
└── labNN-*/                    # instructions + assets you copy into app/
```

Every lab starts the same way. Open a terminal in `app/` and load the
Lab 0 setup:

```powershell
cd existing-harnesses\claude-code\app
. ..\claude-code.env.ps1
```

```sh
cd existing-harnesses/claude-code/app
source ../claude-code.env.sh
```

Always run `claude` **from `app/`**, never from the repo root. Claude Code
reads `CLAUDE.md`, `.claude/` settings and git state from where it
starts, and you want only the practice app in scope.

**Checkpoints are git tags.** Each lab ends with `git tag labNN-done`, and
each lab README states which tag it starts from. The model's output varies
between runs, so your code will differ from someone else's. That is
expected; the prompts describe goals, not exact code.

To redo a lab, return to its starting tag:

```powershell
git switch main
git reset --hard lab02a-done   # the tag the lab starts from
git clean -fd                  # remove untracked files (keeps gitignored .env, .runs)
```

If you fall far behind, or your app drifted too far to follow along,
re-run [Lab 2A](lab02-tool-loop/) from `lab00-done`.

## Seeing what the harness did

In interactive mode, each tool call appears inline above the answer, as
lines like `⏺ Bash(python -m pytest -q)` or `⏺ Update(pricing.py)`. Press
`Ctrl+O` to expand a collapsed tool result. In headless mode
(`claude -p "..."`) only the final answer prints, unless you add
`--output-format stream-json --verbose` (used from Lab 7 on). Every
session is also saved as a JSONL transcript under
`~/.claude/projects/<encoded-app-path>/` (`%USERPROFILE%\.claude\projects\...`
on Windows).

## Safety

Use only the synthetic data these labs create. Plan mode, `CLAUDE.md`, and
`.claude/rules/` are instructions, **not** security boundaries. Permission
rules and hooks are enforcement, but only for the tools and patterns they
match (Lab 6 shows the gaps). Do not point the agent at real files,
production resources or secrets. Never commit keys or tokens, or paste them
into prompts or transcripts. Live runs use your Foundry quota and may incur
charges. The cost figures Claude Code reports are list-price estimates, not
your bill. Record unavailable metrics as unavailable. The build-your-own
labs remain Entra-only.
