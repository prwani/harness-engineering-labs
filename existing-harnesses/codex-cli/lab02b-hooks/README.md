# Lab 2B — Hooks and command policy

**Capability:** Codex has execution-policy rules and hooks. A prefix rule
matches *commands*, not every tool type; it does not replace the build-your-own
`pre_tool`/`pre_model` hooks or validate model transcript invariants.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in the
endpoint ending in `/openai/v1` and deployment. Provide `AZURE_OPENAI_API_KEY`
through your resource key from a secret manager. The
[Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex. Never save the key in the
repository. **Workspace:** start in `lab02b-hooks/` and follow the
[common preflight](../#workspace-and-preflight). Initialize the synthetic
workspace as its own repository (not the course checkout), then copy
**this lab's** policy to the private home:

```powershell
git -C "$workdir" init
New-Item -ItemType Directory -Path (Join-Path $env:CODEX_HOME 'rules') | Out-Null
Copy-Item .\commands.rules (Join-Path $env:CODEX_HOME 'rules\commands.rules')
```

```sh
git -C "$workdir" init
mkdir -p "$CODEX_HOME/rules"
cp commands.rules "$CODEX_HOME/rules/commands.rules"
```

Check the rules *without executing anything* (`execpolicy` is available
in 0.159.3 even though top-level help does not list it):

The following commands work in both PowerShell and bash, from the lab directory:

```sh
codex execpolicy check --rules commands.rules -- rm test.txt
codex execpolicy check --rules commands.rules -- git status
codex execpolicy check --rules commands.rules -- git commit
```

Expect forbidden, allow and no matching rule, respectively. Start
`codex -C "$workdir" --sandbox read-only` in either shell and, in that
interactive session, ask Codex to read `git status`; compare
the tool choice to the policy result. Never delete files just to test a rule.

Inspect [Codex's execution policy documentation](https://developers.openai.com/codex/exec-policy)
and your installed version before using rules in production. The supplied
`rm` rule does **not** block every way to delete a file (for example Python,
`unlink`, or another tool). `git status` is allowed as a prefix, not a
whitelist for all commands; sandboxing and approval still apply. Never run
with `--ignore-rules`. For comprehensive authorization, enforce resource-
scoped policy *outside* the model/harness; do not claim this lab enforces
the build-your-own Lab 2B command policy. Record actual rule behavior or
mark it unverified on your version.

Follow [reset and cleanup](../#reset-and-cleanup) afterward; this also
removes the workspace's synthetic `.git` directory, not the course repo's.
