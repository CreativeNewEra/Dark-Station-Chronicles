import importlib
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from src.game_logic.story_manager import StoryManager
import src.api.main as main


def create_client(monkeypatch):
    module = importlib.reload(main)

    mock_ai = MagicMock()
    mock_ai.current_backend = "claude"
    mock_ai.get_ai_response.return_value = "ai"
    mock_ai.switch_backend.return_value = True
    story_manager = StoryManager()
    monkeypatch.setitem(
        module.app.dependency_overrides, module.get_ai_manager, lambda: mock_ai
    )
    def override_story_manager(
        request: main.Request, response: main.Response
    ) -> main.StoryManager:
        return story_manager

    monkeypatch.setitem(
        module.app.dependency_overrides,
        module.get_story_manager,
        override_story_manager,
    )

    client = TestClient(module.app)
    return client, module, story_manager, mock_ai


def test_start_game(monkeypatch):
    client, module, story_manager, mock_ai = create_client(monkeypatch)
    expected = story_manager.get_opening_text()
    response = client.get("/game/start")
    assert response.status_code == 200
    assert response.json()["message"] == expected
    assert response.json()["game_state"] is not None


def test_process_command_with_ai(monkeypatch):
    client, module, story_manager, mock_ai = create_client(monkeypatch)
    base = story_manager.process_command("look")
    response = client.post(
        "/game/command",
        json={"command": "look", "use_ai": True, "model": "claude"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"{base}\n\nai"
    mock_ai.get_ai_response.assert_called_once()


def test_switch_model(monkeypatch):
    client, module, _, mock_ai = create_client(monkeypatch)
    response = client.post("/game/switch-model", json={"model": "llama"})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully switched to llama"}
    mock_ai.switch_backend.assert_called_with("llama")


def test_switch_model_new_backend(monkeypatch):
    client, module, _, mock_ai = create_client(monkeypatch)
    response = client.post("/game/switch-model", json={"model": "openai"})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully switched to openai"}
    mock_ai.switch_backend.assert_called_with("openai")
