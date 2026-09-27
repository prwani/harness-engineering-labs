from types import SimpleNamespace

from harness.models import MessagesAdapter, ResponsesAdapter


def test_messages_adapter_preserves_tool_use_id():
    response = SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", id="toolu_1", name="read_file", input={"path": "a"})],
        stop_reason="tool_use",
        usage=SimpleNamespace(input_tokens=3, output_tokens=2, cache_read_input_tokens=1, cache_creation_input_tokens=0),
    )
    turn = MessagesAdapter(SimpleNamespace(messages=SimpleNamespace(create=lambda **_: response)), "model").complete(
        system="", messages=[], tools=[]
    )
    assert turn.stop == "tool"
    assert turn.tool_calls[0].id == "toolu_1"


def test_responses_adapter_uses_call_id_not_item_id():
    response = SimpleNamespace(
        output=[SimpleNamespace(type="function_call", id="fc_1", call_id="call_1", name="read_file", arguments='{"path":"a"}')],
        status="completed",
        usage=SimpleNamespace(input_tokens=3, output_tokens=2, input_tokens_details=SimpleNamespace(cached_tokens=1)),
    )
    turn = ResponsesAdapter(SimpleNamespace(responses=SimpleNamespace(create=lambda **_: response)), "model").complete(
        system="", messages=[], tools=[]
    )
    assert turn.stop == "tool"
    assert turn.tool_calls[0].id == "call_1"
    assert turn.tool_calls[0].item_id == "fc_1"
