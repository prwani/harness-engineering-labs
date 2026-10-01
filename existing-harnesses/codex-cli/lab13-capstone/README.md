# Lab 13 — Planner, generator, evaluator capstone

**Capability:** Codex can run distinct agent sessions with file handoffs;
the dynamic graph, skeptic evaluator, bounded refinement and ablation
below are **human-orchestrated**, not a built-in Codex workflow engine.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint, deployment and API version. Provide `AZURE_OPENAI_API_KEY`
through a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported, or your own resource key from a secret manager; never save it
in files. Start in this lab's directory and prepare synthetic data:

```sh
workdir="$(mktemp -d)"
mkdir -p "$workdir/.agents/skills/product-description"
cp product-description/SKILL.md "$workdir/.agents/skills/product-description/"
printf 'id,name,material,use\n1,Demo bowl,ceramic,feeding\n2,Demo leash,nylon,walking\n' > "$workdir/products.csv"
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
   Compare against a fresh run *without* the skill (ablation). Record
   success, token usage when reported and the exit reason.

The handoff files are local scratch artifacts, not an approved catalog
write. A production dynamic graph would need external scheduling, audit,
idempotency, policy and objective grading. Do not submit changes to a
real store or assume model-based evaluation proves safety.
