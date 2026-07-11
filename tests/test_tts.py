"""Unit tests for TTSService."""

import httpx
import pytest

from tts import TTSService, VOICES


class FakeResponse:
    def __init__(self, status_code=200, content=b"fake-mp3-bytes"):
        self.status_code = status_code
        self.content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)


@pytest.mark.asyncio
async def test_speak_returns_audio_bytes(monkeypatch):
    async def fake_post(self, url, json, headers):
        assert VOICES["posh"]["voice_id"] in url
        assert headers["xi-api-key"] == "test-key"
        return FakeResponse(200, b"audio-data")

    monkeypatch.setattr("tts.settings.elevenlabs_api_key", "test-key")
    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    service = TTSService()
    audio = await service.speak("Hark!", "posh")

    assert audio == b"audio-data"


@pytest.mark.asyncio
async def test_speak_raises_on_401(monkeypatch):
    async def fake_post(self, url, json, headers):
        return FakeResponse(401, b"")

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    service = TTSService()
    with pytest.raises(ValueError, match="Invalid ElevenLabs API key"):
        await service.speak("Hark!", "posh")


@pytest.mark.asyncio
async def test_speak_raises_on_server_error(monkeypatch):
    async def fake_post(self, url, json, headers):
        return FakeResponse(500, b"")

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    service = TTSService()
    with pytest.raises(httpx.HTTPStatusError):
        await service.speak("Hark!", "posh")


def test_all_voices_have_required_fields():
    for key, voice in VOICES.items():
        assert "name" in voice
        assert "emoji" in voice
        assert "voice_id" in voice
        assert voice["voice_id"]
