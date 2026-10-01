# Lab 13 — Planner, generator and evaluator

Use this lab's `foundry.env.example` and the [preflight](../). In an
isolated workspace add synthetic `product.txt` (ceramic bowl for
pet feeding) and `catalog.csv` (bowl price 20). Run three separately
identified stages: ask a planner for a short evidence plan; ask a
generator for a two-sentence description based only on the sources;
ask an evaluator in a **fresh context**, without the generator's
private reasoning, to check each claim against the files. Reject
unsupported claims and allow at most one manual revision.

Record which stage ran, the supplied evidence, verdict and revision
count. CLI subagents can help divide tasks, but independent evaluator
context and human stop conditions must be established explicitly.
Do not claim a native, scored planner–generator–evaluator graph.
