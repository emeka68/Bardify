"""Shared pytest fixtures for the Bardify test suite."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

import main
from transformer import ShakespeareTransformer


def make_anthropic_response(text: str, input_tokens: int = 10, output_tokens: int = 10):
    """Build a fake object shaped like an Anthropic messages.create() response."""
    return SimpleNamespace(
        content=[SimpleNamespace(text=text)],
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


@pytest.fixture
def client():
    """FastAPI TestClient for the app."""
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Ensure rate-limit state doesn't leak between tests."""
    main.request_times.clear()
    yield
    main.request_times.clear()


@pytest.fixture(autouse=True)
def reset_caches():
    """Ensure cache state doesn't leak between tests."""
    main.transform_cache.clear()
    main.tts_cache.clear()
    yield
    main.transform_cache.clear()
    main.tts_cache.clear()


@pytest.fixture(autouse=True)
def reset_stats():
    """Ensure usage counters don't leak between tests."""
    main.stats.reset()
    yield
    main.stats.reset()


@pytest.fixture
def mock_transformer(monkeypatch):
    """Patch the global transformer instance's Anthropic client."""
    fake_client = MagicMock()
    monkeypatch.setattr(main.transformer, "client", fake_client)
    return fake_client


@pytest.fixture
def transformer_instance(monkeypatch):
    """A standalone ShakespeareTransformer with a mocked Anthropic client."""
    instance = ShakespeareTransformer()
    instance.client = MagicMock()
    return instance
