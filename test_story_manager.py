import pytest

from src.game_logic.story_manager import StoryManager


@pytest.fixture
def manager():
    return StoryManager()


def test_movement_valid_path(manager):
    response = manager.process_command("north")
    assert manager.current_room == "corridor"
    assert "You move north." in response
    assert manager.rooms["corridor"].description in response


def test_movement_invalid_exit(manager):
    manager.current_room = "corridor"
    response = manager.process_command("east")
    assert response == "You cannot go east from here."
    assert manager.current_room == "corridor"


def test_select_class_valid(manager):
    response = manager.process_command("/select-class cybernetic")
    assert response == "You have chosen the cybernetic class. Your journey begins..."
    assert manager.player.character_class == "cybernetic"


def test_select_class_case_insensitive(manager):
    response = manager.process_command("/select-class Psionic")
    assert response == "You have chosen the psionic class. Your journey begins..."
    assert manager.player.character_class == "psionic"


def test_select_class_invalid(manager):
    response = manager.process_command("/select-class wizard")
    assert response == "Invalid class. Choose from: cybernetic, psionic, or hunter."
    assert manager.player.character_class is None


def test_select_class_missing_argument(manager):
    response = manager.process_command("/select-class")
    assert response == "Invalid class. Choose from: cybernetic, psionic, or hunter."
    assert manager.player.character_class is None


def test_examine_room(manager):
    response = manager.process_command("examine room")
    assert response == manager.rooms[manager.current_room].description


def test_examine_self(manager):
    response = manager.process_command("examine self")
    assert "Health:" in response and "Energy:" in response and "Level:" in response


def test_examine_unknown_target(manager):
    response = manager.process_command("examine door")
    assert (
        response == "You examine the door, but find nothing particularly interesting."
    )


def test_examine_no_target(manager):
    response = manager.process_command("examine")
    assert response == "You examine the , but find nothing particularly interesting."
