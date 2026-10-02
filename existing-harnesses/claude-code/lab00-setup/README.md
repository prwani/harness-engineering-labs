# Lab 0 — Configure Claude Code with Foundry

This lab is the **one-time setup** for the whole Claude Code track. You do
this once here, then every other lab (1–14) just reuses what you create
in this folder — you won't repeat Foundry configuration again. These
steps follow the official
[Configure Claude Code for Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code?tabs=bash)
guide; read it if you want the full background (model deployment,
permissions, VS Code extension, CI/CD).

## 0. Prerequisites

- A Microsoft Foundry project with a Claude model deployed (for example
  `claude-sonnet-4-6`), and either **Contributor**/**Owner** on the Foundry
  resource group (for Entra sign-in) or a **Project API key** copied from
  the Foundry portal's **Home** page.
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
  installed, if you're using Entra ID authentication (recommended).

## 1. Install the Claude Code CLI

```powershell
# Windows / PowerShell
irm https://claude.ai/install.ps1 | iex
claude --version
```

```sh
# macOS / Windows (Git Bash or WSL) / Linux
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

## 2. Create your Foundry env script (once, for every lab)

Find your **Foundry resource name**: in the Foundry portal go to
**Manage > Project details** and copy **Parent resource**.

Create `claude-code.env.ps1` (or `claude-code.env.sh`) **in this
`existing-harnesses/claude-code/` folder** — both filenames are
gitignored, so nothing you put here is ever committed. Every other lab
dot-sources (or sources) this same file instead of repeating setup.

```powershell
# From existing-harnesses/claude-code/
@'
# Source me with:   . .\claude-code.env.ps1
# Then run:         claude
$_root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Optional: scope az login to this folder only (never touches ~/.azure)
$env:AZURE_CONFIG_DIR = Join-Path $_root ".azure-cli"
if (-not (Test-Path $env:AZURE_CONFIG_DIR)) { New-Item -ItemType Directory -Path $env:AZURE_CONFIG_DIR -Force | Out-Null }

# Required: enable Foundry integration
$env:CLAUDE_CODE_USE_FOUNDRY = "1"

# Your Foundry resource name (replace this)
$env:ANTHROPIC_FOUNDRY_RESOURCE = "<your-resource-name>"
# Or, instead of a resource name, the full base URL:
# $env:ANTHROPIC_FOUNDRY_BASE_URL = "https://<your-resource-name>.services.ai.azure.com"

# Optional: only if your deployment names differ from the defaults
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "claude-sonnet-4-6"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "claude-haiku-4-5"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "claude-opus-4-6"

# Only if you are using API-key auth instead of Entra (see step 3):
# $env:ANTHROPIC_FOUNDRY_API_KEY = "<your-foundry-api-key>"

Write-Host "Claude Code configured for Foundry resource '$env:ANTHROPIC_FOUNDRY_RESOURCE'." -ForegroundColor Green
'@ | Set-Content claude-code.env.ps1
```

```sh
# From existing-harnesses/claude-code/
cat > claude-code.env.sh <<'EOF'
# Source me with:   source ./claude-code.env.sh
# Then run:         claude
_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Optional: scope az login to this folder only (never touches ~/.azure)
export AZURE_CONFIG_DIR="$_root/.azure-cli"
mkdir -p "$AZURE_CONFIG_DIR"

# Required: enable Foundry integration
export CLAUDE_CODE_USE_FOUNDRY=1

# Your Foundry resource name (replace this)
export ANTHROPIC_FOUNDRY_RESOURCE="<your-resource-name>"
# Or, instead of a resource name, the full base URL:
# export ANTHROPIC_FOUNDRY_BASE_URL="https://<your-resource-name>.services.ai.azure.com"

# Optional: only if your deployment names differ from the defaults
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-4-6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-6"

# Only if you are using API-key auth instead of Entra (see step 3):
# export ANTHROPIC_FOUNDRY_API_KEY="<your-foundry-api-key>"

echo "Claude Code configured for Foundry resource '$ANTHROPIC_FOUNDRY_RESOURCE'."
EOF
```

Edit the file you just created and replace `<your-resource-name>` (and
model names, if needed) with your real values. Never put an API key
directly in this file if you can avoid it — prefer Entra (step 3, option
A) so no secret ever touches disk.

## 3. Authenticate

**Option A — Microsoft Entra ID (recommended):** dot-source/source the
script first (so `AZURE_CONFIG_DIR` scopes the login to this folder),
then sign in:

```powershell
. .\claude-code.env.ps1
az login            # add --tenant <tenant-id> if Foundry is in another tenant
az account show     # confirm the right subscription
```

```sh
source ./claude-code.env.sh
az login
az account show
```

Claude Code detects the Azure CLI session automatically; `/login` and
`/logout` inside Claude Code are disabled under Foundry.

**Option B — API key:** copy the **Project API key** from the Foundry
portal's **Home** page, uncomment the `ANTHROPIC_FOUNDRY_API_KEY` line in
your env script, and re-source it. Don't combine both options.

## 4. Create the practice app (once, for every lab)

All later labs work in **one** small app that you grow lab by lab. Create
it as its own git repository next to your env script. `app/` is
gitignored by this course repo, so nothing you build there is committed
here.

```powershell
# From existing-harnesses/claude-code/
New-Item -ItemType Directory app | Out-Null
cd app
git init -b main
"# Pet store practice app`n`nSynthetic data only. Built with Claude Code during the harness labs." | Set-Content README.md
".env`n.env.*`n.runs/`n__pycache__/`n.pytest_cache/`n*.log`n.claude/settings.local.json`n.claude/worktrees/" | Set-Content .gitignore
git add . ; git commit -m "chore: start practice app"
git tag lab00-done
```

```sh
# From existing-harnesses/claude-code/
mkdir app && cd app
git init -b main
printf '# Pet store practice app\n\nSynthetic data only. Built with Claude Code during the harness labs.\n' > README.md
printf '.env\n.env.*\n.runs/\n__pycache__/\n.pytest_cache/\n*.log\n.claude/settings.local.json\n.claude/worktrees/\n' > .gitignore
git add . && git commit -m "chore: start practice app"
git tag lab00-done
```

From now on, every lab starts in `app/` by loading this setup. You never
edit the env script again:

```powershell
cd existing-harnesses\claude-code\app
. ..\claude-code.env.ps1
```

```sh
cd existing-harnesses/claude-code/app
source ../claude-code.env.sh
```

## 5. Verify a live call

Still in `app/`, start Claude Code:

```powershell
claude
```

The first time, Claude Code asks whether you trust this folder; answer
yes, because it is your practice app. This matters later: until a
folder is trusted interactively, Claude Code ignores its project
`permissions.allow` rules, even in headless `claude -p` runs. It must **not** ask you to log in
or choose an Anthropic account. If it does, the env script wasn't loaded
in this terminal (check with `$env:CLAUDE_CODE_USE_FOUNDRY` or
`echo $CLAUDE_CODE_USE_FOUNDRY`).

Ask:

```text
What is this project, according to its README? Answer in one sentence.
```

Then run `/status` and confirm that the API provider is Microsoft Foundry
and the model is your deployment. Record the authentication method, but
never the credential. A successful `az login` is not proof of a working
model call; this answered prompt is. Exit with `/exit`.

**Done when:** `git tag` lists `lab00-done` and the prompt above was
answered through Foundry.
