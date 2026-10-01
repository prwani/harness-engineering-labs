# Lab 2B — Hooks and command policy

**Capability:** Codex has execution-policy rules and hooks. A prefix rule
matches *commands*, not every tool type; it does not replace the build-your-own
`pre_tool`/`pre_model` hooks or validate model transcript invariants.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in the
endpoint ending in `/openai/v1` and deployment. Provide `AZURE_OPENAI_API_KEY`
through a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported. For a resource key, replace `env_key` with
`env_http_headers = { "api-key" = "AZURE_OPENAI_API_KEY" }` in the copied config
and load the key via a secret manager. Never save either credential in the
repository. Make a fresh disposable worktree, then load
this lab's `commands.rules` into the isolated home (not your global config):

```sh
workdir="$(mktemp -d)"
git -C "$workdir" init
mkdir -p "$CODEX_HOME/rules"
cp commands.rules "$CODEX_HOME/rules/commands.rules"
```

Check the rules *without executing anything* (`execpolicy` is available
in 0.159.3 even though top-level help does not list it):

```sh
codex execpolicy check --rules commands.rules -- rm test.txt
codex execpolicy check --rules commands.rules -- git status
codex execpolicy check --rules commands.rules -- git commit
```

Expect forbidden, allow and no matching rule, respectively. Then in an
interactive, read-only session, ask Codex to read `git status`; compare
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
