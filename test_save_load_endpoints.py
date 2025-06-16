import importlib
import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.game_logic import story_manager as sm
import src.api.main as main


def create_client(monkeypatch, tmp_path):
    monkeypatch.setattr(sm, "SAVE_DIR", str(tmp_path))
    module = importlib.reload(main)
    monkeypatch.setattr(module, "SAVE_DIR", str(tmp_path), raising=False)

    mock_ai = MagicMock()
    mock_ai.current_backend = "claude"
    mock_ai.get_ai_response.return_value = "ai"
    mock_ai.switch_backend.return_value = True

    story = module.StoryManager()
    monkeypatch.setitem(
        module.app.dependency_overrides, module.get_ai_manager, lambda: mock_ai
    )
    def override_story_manager() -> main.StoryManager:
        return story

    monkeypatch.setitem(
        module.app.dependency_overrides,
        module.get_story_manager,
        override_story_manager,
    )

    client = TestClient(module.app)
    return client, module, story


def test_save_game_invalid_filename(monkeypatch, tmp_path):
    client, module, _ = create_client(monkeypatch, tmp_path)
    response = client.post("/game/save", json={"filename": "bad*name"})
    assert response.status_code == 500
    assert "invalid filename" in response.json()["detail"].lower()


def test_load_game_not_found(monkeypatch, tmp_path):
    client, module, _ = create_client(monkeypatch, tmp_path)
    response = client.post("/game/load", json={"filename": "missing.json"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_load_game_corrupted(monkeypatch, tmp_path):
    client, module, _ = create_client(monkeypatch, tmp_path)
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not: valid")
    response = client.post("/game/load", json={"filename": "bad.json"})
    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower()


def test_list_saves_handles_getmtime_error(monkeypatch, tmp_path):
    client, module, _ = create_client(monkeypatch, tmp_path)
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{}")

    orig_getmtime = os.path.getmtime

    def fake_getmtime(path):
        if path == str(bad_file):
            raise OSError("broken")
        return orig_getmtime(path)

    monkeypatch.setattr(module.os.path, "getmtime", fake_getmtime)

    response = client.get("/game/saves")
    assert response.status_code == 200
    assert {"filename": "bad.json", "timestamp": "Unknown"} in response.json()

