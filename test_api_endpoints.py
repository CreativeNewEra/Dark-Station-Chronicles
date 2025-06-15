import importlib
import os
import sys
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


def create_client(monkeypatch):
    sys.path.insert(0, os.path.abspath("src"))
    module = importlib.import_module("src.api.main")
    importlib.reload(module)

    mock_ai = MagicMock()
    mock_ai.current_backend = "claude"
    mock_ai.get_ai_response.return_value = "ai"
    mock_ai.switch_backend.return_value = True
    monkeypatch.setattr(module, "ai_manager", mock_ai)

    client = TestClient(module.app)
    return client, module, mock_ai


def test_start_game(monkeypatch):
    client, module, mock_ai = create_client(monkeypatch)
    expected = module.story_manager.get_opening_text()
    response = client.get("/game/start")
    assert response.status_code == 200
    assert response.json()["message"] == expected
    assert response.json()["game_state"] is None


def test_process_command_with_ai(monkeypatch):
    client, module, mock_ai = create_client(monkeypatch)
    base = module.story_manager.process_command("look")
    response = client.post(
        "/game/command",
        json={"command": "look", "use_ai": True, "model": "claude"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"{base}\n\nai"
    mock_ai.get_ai_response.assert_called_once()


def test_switch_model(monkeypatch):
    client, module, mock_ai = create_client(monkeypatch)
    response = client.post("/game/switch-model", json={"model": "llama"})
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully switched to llama"}
    mock_ai.switch_backend.assert_called_with("llama")
