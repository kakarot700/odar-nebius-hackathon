import asyncio

import pytest

from odar.agent import NebiusNemotronAdapter


def test_nebius_messages_translate_tool_use_and_result():
    messages = [
        {"role": "user", "content": "Research this."},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Searching."},
                {"type": "tool_use", "id": "call-1", "name": "web_search", "input": {"query": "test"}},
            ],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "call-1", "content": "Found a page."}],
        },
    ]
    result = NebiusNemotronAdapter._to_openai_messages(messages, "system")
    assert result[0] == {"role": "system", "content": "system"}
    assert result[2]["tool_calls"][0]["function"] == {"name": "web_search", "arguments": '{"query": "test"}'}
    assert result[3] == {"role": "tool", "tool_call_id": "call-1", "content": "Found a page."}


def test_nebius_adapter_maps_tool_call_response(monkeypatch):
    adapter = NebiusNemotronAdapter(api_key="test-key")
    seen = {}

    def fake_post(payload):
        seen.update(payload)
        return {
            "choices": [
                {
                    "message": {
                        "content": "Checking a source.",
                        "tool_calls": [
                            {
                                "id": "call-7",
                                "function": {
                                    "name": "fetch_page",
                                    "arguments": '{"url":"https://example.org"}',
                                },
                            }
                        ],
                    }
                }
            ]
        }

    monkeypatch.setattr(adapter, "_post", fake_post)
    event = asyncio.run(
        adapter.next_response(
            [{"role": "user", "content": "Check this source."}],
            [
                {
                    "name": "fetch_page",
                    "description": "Fetch",
                    "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
                }
            ],
            trace=None,
        )
    )
    assert seen["model"] == adapter.DEFAULT_MODEL
    assert seen["tool_choice"] == "auto"
    assert event.stop_reason == "tool_use"
    assert event.content[0]["text"] == "Checking a source."
    assert event.content[1]["input"] == {"url": "https://example.org"}


def test_nebius_adapter_requires_key(monkeypatch):
    monkeypatch.delenv("NEBIUS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="NEBIUS_API_KEY"):
        NebiusNemotronAdapter()
