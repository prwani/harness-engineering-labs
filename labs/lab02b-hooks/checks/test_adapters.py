from types import SimpleNamespace

import pytest

from harness.models import MessagesAdapter, ResponsesAdapter, ScriptedModel, Turn


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


def test_responses_adapter_preserves_truncation_with_tool_calls():
    response = SimpleNamespace(
        output=[SimpleNamespace(type="function_call", id="fc_1", call_id="call_1", name="read_file", arguments='{}')],
        status="incomplete",
        usage=None,
    )
    turn = ResponsesAdapter(SimpleNamespace(responses=SimpleNamespace(create=lambda **_: response)), "model").complete(
        system="", messages=[], tools=[]
    )
    assert turn.stop == "length"


def test_scripted_model_reports_exhaustion():
    model = ScriptedModel([Turn(text="done")])
    assert model.complete().text == "done"
    with pytest.raises(RuntimeError, match="ran out"):
        model.complete()


def test_messages_adapter_converts_tool_results_and_schemas():
    received = {}
    response = SimpleNamespace(content=[], stop_reason="end", usage=None)

    def create(**kwargs):
        received.update(kwargs)
        return response

    adapter = MessagesAdapter(
        SimpleNamespace(messages=SimpleNamespace(create=create)), "model"
    )
    adapter.complete(
        system="",
        messages=[
            {"role": "user", "content": "read a file"},
            {"role": "assistant", "content": []},
            {"role": "tool", "content": [{"call_id": "call_1", "output": "contents"}]},
        ],
        tools=[{
            "name": "read_file",
            "description": "Read a file",
            "input_schema": {"type": "object", "properties": {}},
        }],
    )

    assert received["messages"][-1]["role"] == "user"
    assert received["messages"][-1]["content"][0]["tool_use_id"] == "call_1"
    assert received["tools"][0]["input_schema"]["type"] == "object"


def test_responses_adapter_converts_tool_results_and_schemas():
    received = {}
    response = SimpleNamespace(output=[], status="completed", usage=None)

    def create(**kwargs):
        received.update(kwargs)
        return response

    adapter = ResponsesAdapter(
        SimpleNamespace(responses=SimpleNamespace(create=create)), "model"
    )
    adapter.complete(
        system="",
        messages=[
            {"role": "user", "content": "read a file"},
            {"role": "assistant", "content": [{
                "type": "function_call", "call_id": "call_1", "name": "read_file",
                "arguments": '{"path":"README.md"}',
            }]},
            {"role": "tool", "content": [{"call_id": "call_1", "output": "contents"}]},
        ],
        tools=[{
            "name": "read_file",
            "description": "Read a file",
            "input_schema": {"type": "object", "properties": {}},
        }],
    )

    assert received["input"][-1] == {
        "type": "function_call_output", "call_id": "call_1", "output": "contents",
    }
    assert received["tools"][0]["parameters"]["type"] == "object"
