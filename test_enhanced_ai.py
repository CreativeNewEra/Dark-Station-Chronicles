from unittest.mock import MagicMock, patch

import pytest

from src.ai.ai_manager import AIManager


@pytest.fixture
def mocked_manager(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    monkeypatch.setenv("LLAMA_MODEL_PATH", "/fake/model.bin")
    monkeypatch.setenv("OPENAI_API_KEY", "openai")
    monkeypatch.setenv("GEMINI_API_KEY", "gem")
    monkeypatch.setenv("OPENROUTER_API_KEY", "router")
    claude_client = MagicMock()
    claude_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="claude")]
    )
    llama_model = MagicMock()
    llama_model.return_value = {"choices": [{"text": "llama"}]}
    openai_client = MagicMock()
    openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="openai"))]
    )
    gem_model = MagicMock()
    gem_model.generate_content.return_value = MagicMock(text="gemini")
    router_client = MagicMock()
    router_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="router"))]
    )
    with patch("src.ai.ai_manager.anthropic.Client", return_value=claude_client), patch(
        "src.ai.ai_manager.os.path.exists", return_value=True
    ), patch("src.ai.ai_manager.Llama", return_value=llama_model), patch(
        "src.ai.ai_manager.openai.OpenAI", side_effect=[openai_client, router_client]
    ), patch("src.ai.ai_manager.genai.GenerativeModel", return_value=gem_model), patch(
        "src.ai.ai_manager.genai.configure"
    ):
        manager = AIManager()
        yield manager, claude_client, llama_model, openai_client, gem_model, router_client


def test_backend_switching(mocked_manager):
    manager, claude_client, llama_model, *_ = mocked_manager
    assert manager.current_backend == "claude"
    assert manager.switch_backend("llama")
    assert manager.current_backend == "llama"
    assert manager.switch_backend("claude")
    assert manager.current_backend == "claude"


def test_game_responses(mocked_manager):
    manager, claude_client, llama_model, openai_client, gem_model, router_client = mocked_manager
    game_state = {
        "current_room": "bridge",
        "player_stats": {"health": 100},
        "inventory": [],
    }
    manager.switch_backend("claude")
    assert manager.get_ai_response("look", game_state) == "claude"
    claude_client.messages.create.assert_called()

    manager.switch_backend("llama")
    assert manager.get_ai_response("look", game_state) == "llama"
    llama_model.assert_called()

    manager.switch_backend("openai")
    assert manager.get_ai_response("look", game_state) == "openai"
    openai_client.chat.completions.create.assert_called()

    manager.switch_backend("gemini")
    assert manager.get_ai_response("look", game_state) == "gemini"
    gem_model.generate_content.assert_called()

    manager.switch_backend("openrouter")
    assert manager.get_ai_response("look", game_state) == "router"
    router_client.chat.completions.create.assert_called()


def test_fallback_to_llama(mocked_manager):
    manager, claude_client, llama_model, *_ = mocked_manager
    manager.switch_backend("claude")
    # Invalidate claude by removing client
    manager.backends["claude"].client = None
    response = manager.get_ai_response("hello")
    assert response == "llama"
    llama_model.assert_called()


def test_switch_backend_invalid_name(mocked_manager):
    manager, *_ = mocked_manager
    assert not manager.switch_backend("invalid")
    assert manager.current_backend == "claude"


def test_switch_backend_unavailable(mocked_manager):
    manager, *_ = mocked_manager
    # Make llama unavailable
    manager.backends["llama"].model = None
    assert not manager.switch_backend("llama")
    assert manager.current_backend == "claude"
