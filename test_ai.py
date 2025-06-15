from unittest.mock import MagicMock, patch

import pytest

from src.ai.ai_manager import ClaudeBackend, LlamaBackend


@pytest.fixture
def mock_anthropic():
    """Mock anthropic.Client used by ClaudeBackend."""
    fake_client = MagicMock()
    fake_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="mocked claude response")]
    )
    with patch("src.ai.ai_manager.anthropic.Client", return_value=fake_client):
        yield fake_client


def test_claude_backend_generate_response(monkeypatch, mock_anthropic):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    backend = ClaudeBackend()
    assert backend.is_available()
    response = backend.generate_response("Hello")
    assert response == "mocked claude response"
    mock_anthropic.messages.create.assert_called_once()


@pytest.fixture
def mock_llama(monkeypatch):
    monkeypatch.setenv("LLAMA_MODEL_PATH", "/fake/model.bin")
    fake_model = MagicMock()
    fake_model.return_value = {"choices": [{"text": "mocked llama"}]}
    with patch("src.ai.ai_manager.os.path.exists", return_value=True), patch(
        "src.ai.ai_manager.Llama", return_value=fake_model
    ):
        yield fake_model


def test_llama_backend_generate_response(mock_llama):
    backend = LlamaBackend()
    assert backend.is_available()
    response = backend.generate_response("Hi")
    assert response == "mocked llama"
    mock_llama.assert_called_once()
