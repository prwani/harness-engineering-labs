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

## Workspace and preflight

Every lab includes `workspace/` with only a tracked `.gitkeep`; generated
contents are gitignored. Comparison labs also include `workspace-b/`.
These folders make paths predictable, **not** an OS isolation boundary.
Codex can inherit parent `AGENTS.md`, discover skills, and access other
readable files. Run write drills only on synthetic data; use an isolated
account/container when real host files must be protected.

**Start each lab's commands in that lab's directory**, not the track root
or a previous workspace. Run the following preflight in your chosen shell
for every lab (and before a completely fresh attempt):

```powershell
$labdir = (Get-Location).Path
$workdir = Join-Path $labdir 'workspace'
$env:CODEX_HOME = Join-Path ([IO.Path]::GetTempPath()) ("codex-lab-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $env:CODEX_HOME | Out-Null
Copy-Item .\config.toml.example (Join-Path $env:CODEX_HOME 'config.toml')
```

```sh
labdir="$PWD"
workdir="$labdir/workspace"
export CODEX_HOME="$(mktemp -d)"
chmod 700 "$CODEX_HOME"
cp ./config.toml.example "$CODEX_HOME/config.toml"
```

Edit **this temporary config**, setting your deployment and endpoint
(`/openai/v1`). Keep credentials out of it. Use a fresh `CODEX_HOME` for
each lab; keep the same home for that lab's resume exercise. Resetting a
workspace does **not** erase session history in `CODEX_HOME`.

Load your own resource API key into
`AZURE_OPENAI_API_KEY` via a secret manager; `env_key` in the config
names that variable. The
[Microsoft Foundry Codex guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
currently says Entra ID is **not supported for Codex**; do not pass an
Entra token in place of a key. Never write the key
to a lab file, terminal transcript, or commit. For noninteractive runs use
`--sandbox read-only` unless a lab explicitly requires **disposable local**
writes. A read-only sandbox restricts writes; it does *not* disable tools,
network access, the model's built-in agent loop, or all connectors. It is
not a confidentiality boundary for other readable host files or environment
variables. Use a separate disposable account/container for sensitive
environments, and do not give Codex access to real customer data.

Use only synthetic data and disposable directories. Do not grant access to
real customer data, live Azure resources, or privileged credentials. After
each lab, reset the disposable workspace, remove `CODEX_HOME` and unset the
credential. Record unsupported metrics as **unavailable**, not zero.

On Windows, enter the key without putting its literal value in history:

```powershell
$secureKey = Read-Host 'Azure OpenAI API key' -AsSecureString
$env:AZURE_OPENAI_API_KEY = [Net.NetworkCredential]::new('', $secureKey).Password
$secureKey.Dispose()
Remove-Variable secureKey
```

In bash, use a secret manager or a hidden prompt:

```sh
read -r -s -p 'Azure OpenAI API key: ' AZURE_OPENAI_API_KEY
printf '\n'
export AZURE_OPENAI_API_KEY
```

The key is available to processes launched from **this shell**, not other
already-running terminals. Never print it. In the temporary config, add
the following to keep the key out of model-launched shell tools (Codex
itself still needs the environment variable for provider authentication):

```toml
[shell_environment_policy]
exclude = ["AZURE_OPENAI_API_KEY"]
```

### Native Windows prerequisite

Native Windows learners need a functioning Windows sandbox before the
file/tool exercises. A successful model reply alone does **not** verify
that shell tools can read the fixtures. Follow the
[official Windows sandbox guide](https://developers.openai.com/codex/windows/).
In each temporary Windows config, select the preferred implementation:

```toml
[windows]
sandbox = "elevated"
```

Launch interactive `codex -C "$workdir" --sandbox read-only`. Complete the
offered sandbox setup. Newer versions expose `/setup-default-sandbox`
**inside Codex**, not PowerShell; check the `/` menu rather than assuming
that command exists (it is not available in 0.157.0). Administrator
approval may be required to create
the low-privilege sandbox users and configure firewall/local policy.
Normal lab sessions do not need to run the terminal as administrator.
Check setup whenever you create a new private `CODEX_HOME`; the CLI may
need to provision sandbox state for that home again.

If your organization disallows elevated setup, ask IT or use WSL with its
Linux prerequisites. The documented `unelevated` Windows fallback has
weaker isolation and should be an explicit learner/administrator decision,
not an automatic downgrade. Do not fix `blocked by policy` errors by
disabling the sandbox or blanket-allowing commands. Follow Lab 0's
file-read check before progressing. macOS/Linux/WSL learners do not need
this Windows-specific setup.

If an embedded terminal reports `host Job Object prevents daemon
detachment`, rerun the interactive command with `--no-daemon`, as the CLI
error instructs, for example `codex --no-daemon -C "$workdir" --sandbox
read-only`. This keeps the app server attached to the session; it does
not disable the sandbox. Check your installed version's help/error before
using this compatibility option.

### Reset and cleanup

Exit Codex first. From `existing-harnesses/codex-cli/`, reset only the lab
you are about to rerun. These scripts prompt before deleting contents:

```powershell
.\scripts\reset-workspace.ps1 -Lab lab08-skills-tools
.\scripts\reset-workspace.ps1 -Lab lab08-skills-tools -Second
```

```sh
bash ./scripts/reset-workspace.sh lab08-skills-tools
bash ./scripts/reset-workspace.sh lab08-skills-tools --second
```

They preserve `.gitkeep`, reject unknown lab names and linked workspaces,
and do not modify other labs or your usual Codex home. Reset both folders
before a comparison; use a new `codex exec` invocation for a fresh context,
not `resume`. Where a lab asks for **no project instructions**, also pass
`-c project_doc_max_bytes=0` to disable inherited `AGENTS.md` loading.

At the end of a lab, unset the credential and remove only the private home
created by the preflight above (check the printed path before deleting):

```powershell
Remove-Item Env:\AZURE_OPENAI_API_KEY -ErrorAction SilentlyContinue
$env:CODEX_HOME
# Only after verifying this is the temporary codex-lab-<guid> directory:
Remove-Item -LiteralPath $env:CODEX_HOME -Recurse -Force
Remove-Item Env:\CODEX_HOME
```

```sh
unset AZURE_OPENAI_API_KEY
printf '%s\n' "$CODEX_HOME"
# Only after verifying this is the temporary directory created above:
rm -r -- "$CODEX_HOME"
unset CODEX_HOME
```

Clear generated fixtures and handoffs with the reset helper. Do not delete
the lab folder or repository. Re-run preflight for the next lab.
