# Lab 2B — Hooks and command policy

**Capability:** Codex has execution-policy rules and hooks. A prefix rule
matches *commands*, not every tool type; it does not replace the build-your-own
`pre_tool`/`pre_model` hooks or validate model transcript invariants.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in the
endpoint, deployment and supported API version. Provide `AZURE_OPENAI_API_KEY`
through a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported, or your own resource key via a secret manager; never save either
credential in the repository. Make a fresh disposable worktree, then load
this lab's `commands.rules` into the isolated home (not your global config):

```sh
workdir="$(mktemp -d)"
git -C "$workdir" init
mkdir -p "$CODEX_HOME/rules"
cp commands.rules "$CODEX_HOME/rules/commands.rules"
```

If your version has `codex execpolicy check`, inspect how `rm test.txt`,
`git status` and `git commit` are classified with `--rules commands.rules
-- <command>`. Codex CLI 0.159.3 does **not** expose this check command:
use an interactive, read-only `codex -C "$workdir" --sandbox read-only
--ask-for-approval on-request` and ask it to explain which commands it
would choose for `git status` and removing a synthetic file. Do **not**
attempt an actual deletion to test policy. Use `--json` in a separate
noninteractive read task to inspect which tools are invoked.

Inspect [Codex's execution policy documentation](https://developers.openai.com/codex/exec-policy)
and your installed version before using rules in production. The supplied
`rm` rule does **not** block every way to delete a file (for example Python,
`unlink`, or another tool). `git status` is allowed as a prefix, not a
whitelist for all commands; sandboxing and approval still apply. Never run
with `--ignore-rules`. For comprehensive authorization, enforce resource-
scoped policy *outside* the model/harness; do not claim this lab enforces
the build-your-own Lab 2B command policy. Record actual rule behavior or
mark it unverified on your version.
