"""
TTS Service — ElevenLabs integration.

Converts text to speech using ElevenLabs pre-made voices.
"""

import base64
import httpx
from config import settings


VOICES = {
    "posh":       {"name": "Posh British",  "emoji": "🎩", "voice_id": "onwK4e9ZLuTAKqWW03F9"},
    "roadman":    {"name": "Roadman",        "emoji": "🧢", "voice_id": "ErXwobaYiN019PkySvjV"},
    "villain":    {"name": "Villain",        "emoji": "😈", "voice_id": "VR6AewLTigWG4xSOukaG"},
    "southern":   {"name": "Southern Belle", "emoji": "🌸", "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    "romantic":   {"name": "Romantic",       "emoji": "💕", "voice_id": "21m00Tcm4TlvDq8ikWAM"},
    "theatre":    {"name": "Theatre Kid",    "emoji": "🎬", "voice_id": "MF3mGyEYCl7XYWbV9V6O"},
    "elder":      {"name": "Wise Elder",     "emoji": "🦉", "voice_id": "pNInz6obpgDQGcFmaJgB"},
    "mysterious": {"name": "Mysterious",     "emoji": "🌙", "voice_id": "AZnzlk1XvdvUeBnXmlld"},
}

ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


class TTSService:
    async def speak(self, text: str, voice_key: str) -> bytes:
        voice = VOICES[voice_key]
        url = f"{ELEVENLABS_BASE}/text-to-speech/{voice['voice_id']}"
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        headers = {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code == 401:
                raise ValueError("Invalid ElevenLabs API key")
            resp.raise_for_status()
            return resp.content


tts_service = TTSService()
