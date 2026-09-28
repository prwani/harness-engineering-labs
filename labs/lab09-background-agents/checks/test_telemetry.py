from harness.ledger import Usage
from harness.telemetry import Tracer, cache_breakpoints, cost_for, redact


def test_span_tree_has_expected_shape():
    tracer = Tracer()
    root = tracer.start_run("m1 task")
    iteration = root.child("agent.iteration", index=0)
    iteration.child("gen_ai.chat", provider="claude")
    iteration.child("tool.execute", tool="get_product")
    root.close()

    events = tracer.flatten()

    assert [event["name"] for event in events] == [
        "agent.run", "agent.iteration", "gen_ai.chat", "tool.execute",
    ]


def test_tracing_does_not_mutate_attributes_it_did_not_set():
    tracer = Tracer()
    root = tracer.start_run("task")
    root.child("tool.execute", tool="get_product", args={"id": "1"})

    events = tracer.flatten()

    assert events[1]["attributes"] == {"tool": "get_product", "args": {"id": "1"}}


def test_cost_attribution_scales_with_usage():
    usage = Usage(input_tokens=1000, output_tokens=1000)

    claude_cost = cost_for(usage, "claude")
    gpt_cost = cost_for(usage, "gpt")

    assert claude_cost == 0.018
    assert gpt_cost == 0.02
    assert gpt_cost > claude_cost


def test_redaction_strips_bearer_tokens():
    token = "Bearer" + " " + "abc123DEF456ghi789"
    text = f"calling API with {token} token"

    redacted = redact(text)

    assert "abc123DEF456ghi789" not in redacted
    assert "[REDACTED]" in redacted


def test_redaction_strips_api_keys():
    text = '{"api_key": "secret-value"}'

    redacted = redact(text)

    assert "secret-value" not in redacted
    assert "[REDACTED]" in redacted


def test_redaction_leaves_ordinary_text_untouched():
    text = "product 1 costs $12.50"

    assert redact(text) == text


def test_cache_breakpoints_cover_system_and_tools():
    boundaries = cache_breakpoints("a stable system prompt", [{"name": "get_product"}])

    labels = [boundary.label for boundary in boundaries]

    assert labels == ["system", "tools"]
    assert all(boundary.token_estimate >= 0 for boundary in boundaries)
