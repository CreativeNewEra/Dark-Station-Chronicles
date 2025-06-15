from unittest.mock import MagicMock, patch

import pytest

from src.ai.ai_manager import AIManager


@pytest.fixture
def mocked_manager(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    monkeypatch.setenv("LLAMA_MODEL_PATH", "/fake/model.bin")
    claude_client = MagicMock()
    claude_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="claude")]
    )
    llama_model = MagicMock()
    llama_model.return_value = {"choices": [{"text": "llama"}]}
    with patch("src.ai.ai_manager.anthropic.Client", return_value=claude_client), patch(
        "src.ai.ai_manager.os.path.exists", return_value=True
    ), patch("src.ai.ai_manager.Llama", return_value=llama_model):
        manager = AIManager()
        yield manager, claude_client, llama_model


def test_backend_switching(mocked_manager):
    manager, claude_client, llama_model = mocked_manager
    assert manager.current_backend == "claude"
    assert manager.switch_backend("llama")
    assert manager.current_backend == "llama"
    assert manager.switch_backend("claude")
    assert manager.current_backend == "claude"


def test_game_responses(mocked_manager):
    manager, claude_client, llama_model = mocked_manager
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


def test_fallback_to_llama(mocked_manager):
    manager, claude_client, llama_model = mocked_manager
    manager.switch_backend("claude")
    # Invalidate claude by removing client
    manager.backends["claude"].client = None
    response = manager.get_ai_response("hello")
    assert response == "llama"
    llama_model.assert_called()
