from unittest.mock import MagicMock, patch

import pytest

from src.ai.ai_manager import (
    ClaudeBackend,
    LlamaBackend,
    OpenAIBackend,
    GeminiBackend,
    OpenRouterBackend,
)


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


@pytest.fixture
def mock_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai")
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="openai"))]
    )
    with patch("src.ai.ai_manager.openai.OpenAI", return_value=fake_client):
        yield fake_client


def test_openai_backend_generate_response(mock_openai):
    backend = OpenAIBackend()
    assert backend.is_available()
    response = backend.generate_response("Hi")
    assert response == "openai"
    mock_openai.chat.completions.create.assert_called_once()


@pytest.fixture
def mock_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gem")
    fake_model = MagicMock()
    fake_model.generate_content.return_value = MagicMock(text="gemini")
    with patch("src.ai.ai_manager.genai.GenerativeModel", return_value=fake_model), patch(
        "src.ai.ai_manager.genai.configure"
    ):
        yield fake_model


def test_gemini_backend_generate_response(mock_gemini):
    backend = GeminiBackend()
    assert backend.is_available()
    response = backend.generate_response("Hi")
    assert response == "gemini"
    mock_gemini.generate_content.assert_called_once()


@pytest.fixture
def mock_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "router")
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="router"))]
    )
    with patch("src.ai.ai_manager.openai.OpenAI", return_value=fake_client):
        yield fake_client


def test_openrouter_backend_generate_response(mock_openrouter):
    backend = OpenRouterBackend()
    assert backend.is_available()
    response = backend.generate_response("Hi")
    assert response == "router"
    mock_openrouter.chat.completions.create.assert_called_once()
