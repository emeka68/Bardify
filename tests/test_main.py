"""Integration tests for the FastAPI routes in main.py."""

from unittest.mock import patch

import main


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_root_welcome(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["app"] == "Shakespeare Translator"


def test_transform_success(client):
    fake_result = {
        "original": "hello",
        "transformed": "Good morrow!",
        "timestamp": "2026-01-01T00:00:00",
        "model": "claude-haiku-4-5-20251001",
        "style": "standard",
        "length": "full",
        "usage": {"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
        "error": None,
    }
    with patch.object(main.transformer, "transform", return_value=fake_result):
        resp = client.post("/transform", json={"text": "hello"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["transformed"] == "Good morrow!"
    assert body["error"] is None


def test_transform_empty_text_rejected(client):
    resp = client.post("/transform", json={"text": "   "})
    assert resp.status_code == 400


def test_transform_text_too_long_rejected(client):
    resp = client.post("/transform", json={"text": "x" * 2001})
    assert resp.status_code == 400


def test_transform_invalid_style_rejected(client):
    resp = client.post("/transform", json={"text": "hello", "style": "shakespeare-but-evil"})
    assert resp.status_code == 400


def test_transform_invalid_length_rejected(client):
    resp = client.post("/transform", json={"text": "hello", "length": "extremely-long"})
    assert resp.status_code == 400


def test_transform_propagates_transformer_error(client):
    fake_result = {"error": "API Error: boom", "original": "hello", "transformed": ""}
    with patch.object(main.transformer, "transform", return_value=fake_result):
        resp = client.post("/transform", json={"text": "hello"})

    assert resp.status_code == 500
    assert "boom" in resp.json()["detail"]


def test_rate_limit_enforced(client):
    fake_result = {
        "original": "hi",
        "transformed": "Hark!",
        "timestamp": "2026-01-01T00:00:00",
        "error": None,
    }
    limit = main.settings.rate_limit_per_minute
    with patch.object(main.transformer, "transform", return_value=fake_result):
        for _ in range(limit):
            resp = client.post("/transform", json={"text": "hi"})
            assert resp.status_code == 200

        resp = client.post("/transform", json={"text": "hi"})
        assert resp.status_code == 429


def test_batch_transform(client):
    fake_result = {
        "original": "hi",
        "transformed": "Hark!",
        "timestamp": "2026-01-01T00:00:00",
        "error": None,
    }
    with patch.object(main.transformer, "transform", return_value=fake_result):
        resp = client.post("/batch", json={"texts": ["hi", "there"]})

    assert resp.status_code == 200
    assert resp.json()["count"] == 2


def test_batch_rejects_empty_list(client):
    resp = client.post("/batch", json={"texts": []})
    assert resp.status_code == 400


def test_batch_rejects_over_ten(client):
    resp = client.post("/batch", json={"texts": ["x"] * 11})
    assert resp.status_code == 400


def test_voices_endpoint_lists_all_voices(client):
    resp = client.get("/voices")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["voices"]) == 8
    assert "tts_enabled" in body


def test_speak_without_api_key_returns_503(client, monkeypatch):
    monkeypatch.setattr(main.settings, "elevenlabs_api_key", "")
    resp = client.post("/speak", json={"text": "hello", "voice": "posh"})
    assert resp.status_code == 503


def test_speak_with_invalid_voice_returns_400(client, monkeypatch):
    monkeypatch.setattr(main.settings, "elevenlabs_api_key", "fake-key")
    resp = client.post("/speak", json={"text": "hello", "voice": "not-a-voice"})
    assert resp.status_code == 400


def test_speak_success(client, monkeypatch):
    import base64

    monkeypatch.setattr(main.settings, "elevenlabs_api_key", "fake-key")

    async def fake_speak(text, voice_key):
        return b"fake-audio-bytes"

    with patch.object(main.tts_service, "speak", side_effect=fake_speak):
        resp = client.post("/speak", json={"text": "hello", "voice": "posh"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["voice"] == "posh"
    assert base64.b64decode(body["audio"]) == b"fake-audio-bytes"


def test_config_endpoint_hides_secrets(client):
    resp = client.get("/config")
    body = resp.json()
    assert "anthropic_api_key" not in body
    assert "elevenlabs_api_key" not in body


def test_transform_uses_cache_on_repeated_request(client):
    fake_result = {
        "original": "hello",
        "transformed": "Good morrow!",
        "timestamp": "2026-01-01T00:00:00",
        "style": "standard",
        "length": "full",
        "usage": {"input_tokens": 5, "output_tokens": 5, "total_tokens": 10},
        "error": None,
    }
    with patch.object(main.transformer, "transform", return_value=fake_result) as mock_transform:
        resp1 = client.post("/transform", json={"text": "hello", "style": "standard", "length": "full"})
        resp2 = client.post("/transform", json={"text": "hello", "style": "standard", "length": "full"})

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["transformed"] == resp2.json()["transformed"]
    mock_transform.assert_called_once()


def test_transform_errors_are_not_cached(client):
    fake_error = {"error": "boom", "original": "hello", "transformed": ""}
    with patch.object(main.transformer, "transform", return_value=fake_error) as mock_transform:
        client.post("/transform", json={"text": "hello"})
        client.post("/transform", json={"text": "hello"})

    assert mock_transform.call_count == 2


def test_speak_uses_cache_on_repeated_request(client, monkeypatch):
    monkeypatch.setattr(main.settings, "elevenlabs_api_key", "fake-key")
    call_count = 0

    async def fake_speak(text, voice_key):
        nonlocal call_count
        call_count += 1
        return b"fake-audio-bytes"

    with patch.object(main.tts_service, "speak", side_effect=fake_speak):
        client.post("/speak", json={"text": "hello", "voice": "posh"})
        client.post("/speak", json={"text": "hello", "voice": "posh"})

    assert call_count == 1


def test_stats_endpoint_tracks_usage(client):
    fake_result = {
        "original": "hi",
        "transformed": "Hark!",
        "timestamp": "2026-01-01T00:00:00",
        "style": "dramatic",
        "length": "full",
        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
        "error": None,
    }
    with patch.object(main.transformer, "transform", return_value=fake_result):
        client.post("/transform", json={"text": "hi", "style": "dramatic"})

    resp = client.get("/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["style_usage"]["dramatic"] == 1
    assert body["cache_misses"] == 1
    assert body["cache_hits"] == 0


def test_stats_endpoint_tracks_errors(client):
    fake_error = {"error": "boom", "original": "hi", "transformed": ""}
    with patch.object(main.transformer, "transform", return_value=fake_error):
        client.post("/transform", json={"text": "hi"})

    resp = client.get("/stats")
    assert resp.json()["errors_by_endpoint"]["transform"] == 1
