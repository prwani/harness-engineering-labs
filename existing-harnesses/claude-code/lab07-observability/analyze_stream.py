"""Summarize a `claude -p --output-format stream-json --verbose` run.

Usage: python analyze_stream.py run.jsonl [more.jsonl ...]
Standard library only, so it works without jq.
"""
import collections
import json
import sys


def summarize(path):
    tools = collections.Counter()
    hooks = collections.Counter()
    result = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get("type")
            if kind == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        tools[block.get("name", "?")] += 1
            elif kind == "system" and event.get("subtype") == "hook_response":
                hooks[event.get("hook_event_name") or event.get("hook_name") or event.get("subtype")] += 1
            elif kind == "result":
                result = event

    usage = result.get("usage", {})
    print(f"== {path}")
    print(f"  outcome        : {result.get('subtype', 'unknown')} (is_error={result.get('is_error')})")
    print(f"  turns          : {result.get('num_turns', 'unavailable')}")
    print(f"  wall time (s)  : {result.get('duration_ms', 0) / 1000:.1f}")
    print(f"  input tokens   : {usage.get('input_tokens', 'unavailable')} "
          f"(+cache read {usage.get('cache_read_input_tokens', 0)}, "
          f"cache write {usage.get('cache_creation_input_tokens', 0)})")
    print(f"  output tokens  : {usage.get('output_tokens', 'unavailable')}")
    cost = result.get("total_cost_usd")
    cost = f"{cost:.4f}" if isinstance(cost, (int, float)) else "unavailable"
    print(f"  est. cost (USD): {cost}  (list-price estimate, not your bill)")
    print(f"  tool calls     : {sum(tools.values())} {dict(tools)}")
    if hooks:
        print(f"  hook events    : {dict(hooks)}")
    denials = result.get("permission_denials") or []
    print(f"  denials        : {len(denials)} {[d.get('tool_name') for d in denials]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        summarize(p)
