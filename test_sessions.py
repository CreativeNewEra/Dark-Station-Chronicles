import importlib
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

import src.api.main as main


def create_client(monkeypatch):
    module = importlib.reload(main)
    module.sessions.clear()
    mock_ai = MagicMock()
    mock_ai.current_backend = "claude"
    mock_ai.get_ai_response.return_value = "ai"
    mock_ai.switch_backend.return_value = True
    monkeypatch.setitem(module.app.dependency_overrides, module.get_ai_manager, lambda: mock_ai)
    return TestClient(module.app), module


def test_session_creation(monkeypatch):
    client, module = create_client(monkeypatch)
    response = client.get("/game/start")
    assert response.status_code == 200
    session_id = response.cookies.get("session-id")
    assert session_id in module.sessions


def test_session_reuse(monkeypatch):
    client, module = create_client(monkeypatch)
    client.get("/game/start")
    client.post("/game/command", json={"command": "north", "use_ai": False})
    state = client.get("/game/state")
    assert state.json()["current_room"] == "corridor"
