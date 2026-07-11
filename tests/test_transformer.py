"""Unit tests for ShakespeareTransformer."""

import httpx
from anthropic import APIError

from tests.conftest import make_anthropic_response


def make_api_error(message: str = "rate limited") -> APIError:
    fake_request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return APIError(message, fake_request, body=None)


def test_empty_input_returns_error(transformer_instance):
    result = transformer_instance.transform("")
    assert result["error"] == "Empty input"
    assert result["transformed"] == ""


def test_whitespace_only_input_returns_error(transformer_instance):
    result = transformer_instance.transform("   ")
    assert result["error"] == "Empty input"


def test_text_too_long_returns_error(transformer_instance):
    result = transformer_instance.transform("x" * 2001)
    assert "too long" in result["error"]
    assert result["transformed"] == ""


def test_successful_transform_standard(transformer_instance):
    transformer_instance.client.messages.create.return_value = make_anthropic_response(
        "Hark! What news dost thou bring?"
    )
    result = transformer_instance.transform("What's up?", style="standard", length="full")

    assert result["error"] is None
    assert result["transformed"] == "Hark! What news dost thou bring?"
    assert result["style"] == "standard"
    assert result["length"] == "full"
    assert result["usage"]["total_tokens"] == 20


def test_transform_strips_markdown_and_alternatives(transformer_instance):
    raw = (
        "# Shakespearean Translation\n\n"
        "**I am most weary.**\n\n"
        "---\n\n"
        "### Alternative phrasings:\n"
        "- Weary am I.\n"
    )
    transformer_instance.client.messages.create.return_value = make_anthropic_response(raw)
    result = transformer_instance.transform("I am tired")

    assert "Alternative" not in result["transformed"]
    assert "#" not in result["transformed"]
    assert "---" not in result["transformed"]


def test_transform_takes_only_first_paragraph(transformer_instance):
    raw = "First translation line.\n\nA second unwanted paragraph."
    transformer_instance.client.messages.create.return_value = make_anthropic_response(raw)
    result = transformer_instance.transform("hello")

    assert result["transformed"] == "First translation line."


def test_api_error_is_caught(transformer_instance):
    transformer_instance.client.messages.create.side_effect = make_api_error()
    result = transformer_instance.transform("hello")

    assert result["error"] is not None
    assert "API Error" in result["error"]
    assert result["transformed"] == ""


def test_unexpected_exception_is_caught(transformer_instance):
    transformer_instance.client.messages.create.side_effect = RuntimeError("boom")
    result = transformer_instance.transform("hello")

    assert "Unexpected error" in result["error"]


def test_invalid_style_falls_back_to_standard(transformer_instance):
    transformer_instance.client.messages.create.return_value = make_anthropic_response("ok")
    prompt = transformer_instance._build_system_prompt("not-a-real-style", "full")
    assert "quick-witted Shakespearean translator" in prompt


def test_batch_transform_calls_transform_per_item(transformer_instance, monkeypatch):
    monkeypatch.setattr("transformer.time.sleep", lambda _: None)
    transformer_instance.client.messages.create.return_value = make_anthropic_response("done")

    results = transformer_instance.batch_transform(["a", "b", "c"])

    assert len(results) == 3
    assert all(r["transformed"] == "done" for r in results)
