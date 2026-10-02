# Lab 13 — Planner, generator, evaluator capstone

**Capability:** Codex can run distinct agent sessions with file handoffs;
the dynamic graph, skeptic evaluator, bounded refinement and ablation
below are **human-orchestrated**, not a built-in Codex workflow engine.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Provide
`AZURE_OPENAI_API_KEY` through your resource key from a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab13-capstone/` and follow the
[common preflight](../#workspace-and-preflight). Use `workspace/` for
the three-stage run and `workspace-b/` for the no-skill ablation.
Copy only **this lab's** skill and add matching data:

```powershell
$second = Join-Path $labdir 'workspace-b'
$skilldir = Join-Path $workdir '.agents\skills\product-description'
New-Item -ItemType Directory -Path $skilldir -Force | Out-Null
Copy-Item .\product-description\SKILL.md $skilldir
"id,name,material,use`n1,Demo bowl,ceramic,feeding`n2,Demo leash,nylon,walking" |
  Set-Content (Join-Path $workdir 'products.csv') -Encoding utf8
Copy-Item (Join-Path $workdir 'products.csv') (Join-Path $second 'products.csv')
```

```sh
second="$labdir/workspace-b"
mkdir -p "$workdir/.agents/skills/product-description"
cp product-description/SKILL.md "$workdir/.agents/skills/product-description/"
printf 'id,name,material,use\n1,Demo bowl,ceramic,feeding\n2,Demo leash,nylon,walking\n' > "$workdir/products.csv"
cp "$workdir/products.csv" "$second/products.csv"
```

Each command below is a **fresh session**. Do not use `resume` for the
evaluator. PowerShell:

```powershell
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only `
  -o (Join-Path $workdir 'plan.txt') `
  "Read products.csv and list the ids, attributes and one task per product; do not edit files."
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only `
  -o (Join-Path $workdir 'descriptions.txt') `
  "Read products.csv and plan.txt. Use the product-description skill. Write one factual sentence per product with its id, material and use."
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only `
  "Read only products.csv and descriptions.txt. Independently evaluate factual accuracy and brand-rule compliance per id: one concise sentence, material and use, no invented attributes or medical claims, missing attributes marked unknown. Quote source evidence and flag unsupported claims."
```

Bash:

```sh
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  -o "$workdir/plan.txt" \
  "Read products.csv and list the ids, attributes and one task per product; do not edit files."
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  -o "$workdir/descriptions.txt" \
  "Read products.csv and plan.txt. Use the product-description skill. Write one factual sentence per product with its id, material and use."
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  "Read only products.csv and descriptions.txt. Independently evaluate factual accuracy and brand-rule compliance per id: one concise sentence, material and use, no invented attributes or medical claims, missing attributes marked unknown. Quote source evidence and flag unsupported claims."
```

1. **Planner:** `codex exec --skip-git-repo-check -C "$workdir"
   --sandbox read-only -o "$workdir/plan.txt" "Read products.csv and list
   the ids, attributes and one task per product; do not edit files."`
   Check the plan against the two CSV rows.
2. **Generator:** start a *fresh* `codex exec` session, read
   `products.csv` and `plan.txt`, explicitly use the bundled
   `product-description` skill, and write two candidate descriptions to
   `$workdir/descriptions.txt` using `-o`. Confirm each mentions only supplied
   attributes.
3. **Evaluator:** start a *fresh*, read-only session that reads
   `products.csv` and `descriptions.txt`; ask it to score factual accuracy
   and brand-rule compliance per id, quote evidence, and flag invented
   attributes. Do not reuse the generator session; optionally choose a
   different model if available. **Independently check** evaluator claims
   against the CSV instead of accepting a model score as ground truth.
4. If any item fails, ask the generator for a *single* revision with the
   concrete errors; stop after two revisions or no score improvement.
   Compare against a fresh run in `workspace-b/` *without* the skill
   (ablation): use `-C "$second"` for the same stages, with handoffs in
   that folder and omit the generator's skill instruction. Record
   success, token usage when reported and the exit reason.

The handoff files are local scratch artifacts, not an approved catalog
write. A production dynamic graph would need external scheduling, audit,
idempotency, policy and objective grading. Do not submit changes to a
real store or assume model-based evaluation proves safety.

Follow [reset and cleanup](../#reset-and-cleanup) for both workspaces.
