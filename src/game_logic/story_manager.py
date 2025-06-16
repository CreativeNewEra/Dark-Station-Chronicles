import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict

# Define the path for save files relative to the project root
SAVE_DIR = "saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR, exist_ok=True)


@dataclass
class Player:
    health: int = 100
    energy: int = 100
    level: int = 1
    exp: int = 0
    inventory: List[str] = field(default_factory=list)
    character_class: Optional[str] = None


@dataclass
class Room:
    description: str
    exits: Dict[str, str]  # direction -> room_id mapping


class StoryManager:
    """Handle player state and command processing for the text adventure."""

    def __init__(self):
        """Initialize the player and starting rooms."""
        self.player = Player()
        self.current_room = "start"

        # Initialize rooms
        self.rooms = {
            "start": Room(
                description="You find yourself in the dimly lit reception area of Dark Station. "
                "Emergency lights cast an eerie red glow across abandoned terminals.",
                exits={"north": "corridor", "east": "security"},
            ),
            "corridor": Room(
                description="A long corridor stretches before you. Loose cables hang from the ceiling, "
                "occasionally sparking with residual power.",
                exits={"south": "start", "north": "lab"},
            ),
            "security": Room(
                description="The security office is a mess of broken monitors and scattered datapads. "
                "A powered-down security robot sits motionless in the corner.",
                exits={"west": "start"},
            ),
            "lab": Room(
                description="This appears to be a research laboratory. Strange equipment lines the walls, "
                "and holographic displays flicker with corrupted data.",
                exits={"south": "corridor"},
            ),
        }

    def get_opening_text(self) -> str:
        """Return the introductory text shown at game start."""
        return (
            "Welcome to Dark Station Chronicles!\n\n"
            "In the depths of space, aboard an abandoned research station, your story begins. "
            "Choose your path carefully as you uncover the mysteries that lie within.\n\n"
            "Available character classes:\n"
            "- Cybernetic: Enhanced with advanced technology and neural interfaces\n"
            "- Psionic: Gifted with psychic abilities and enhanced perception\n"
            "- Hunter: Skilled in survival, tracking, and combat techniques\n\n"
            "To begin, select your class with the command: /select-class [classname]\n"
            "Example: /select-class cybernetic\n\n"
            f"{self.rooms[self.current_room].description}"
        )

    def process_command(self, command: str) -> str:
        """Interpret and execute a player command."""
        command = command.lower().strip()

        # Handle movement
        if command in ["north", "south", "east", "west"]:
            return self._handle_movement(command)

        # Handle looking around
        elif command in ["look", "look around"]:
            return self.rooms[self.current_room].description

        # Handle examining
        elif command.startswith("examine"):
            return self._handle_examine(command)

        # Handle class selection
        elif command.startswith("/select-class"):
            return self._handle_class_selection(command)

        # Default response
        return "I don't understand that command."

    def _handle_movement(self, direction: str) -> str:
        """Handle moving the player between rooms.

        Parameters
        ----------
        direction: str
            Cardinal direction requested by the player.

        Returns
        -------
        str
            Description of the new room if the exit exists, otherwise an error
            message.
        """
        current_room = self.rooms[self.current_room]
        if direction in current_room.exits:
            self.current_room = current_room.exits[direction]
            return (
                f"You move {direction}.\n\n{self.rooms[self.current_room].description}"
            )
        return f"You cannot go {direction} from here."

    def _handle_examine(self, command: str) -> str:
        """Provide information about the specified target.

        Parameters
        ----------
        command: str
            Full examine command issued by the player.

        Returns
        -------
        str
            Description of the current room, player stats, or a generic message
            depending on the target.
        """
        target = command[8:].strip()  # Remove "examine " from the start

        # Add some basic examination responses
        if target == "room" or target == "area":
            return self.rooms[self.current_room].description
        elif target == "self":
            return f"Health: {self.player.health}%\nEnergy: {self.player.energy}%\nLevel: {self.player.level}"

        return f"You examine the {target}, but find nothing particularly interesting."

    def _handle_class_selection(self, command: str) -> str:
        """Set the player's class based on the selection command.

        Parameters
        ----------
        command: str
            Command containing the desired class name.

        Returns
        -------
        str
            Confirmation text if the class is valid or an error message.
        """
        class_name = command.split()[-1].lower()
        valid_classes = ["cybernetic", "psionic", "hunter"]

        if class_name in valid_classes:
            self.player.character_class = class_name
            return f"You have chosen the {class_name} class. Your journey begins..."

        return "Invalid class. Choose from: cybernetic, psionic, or hunter."

    def save_game(self, filename: str) -> str:
        """Saves the current game state to a JSON file."""
        import re

        # Only allow filenames with alphanumerics, underscores, hyphens, and .json extension
        if not re.fullmatch(r"[A-Za-z0-9_\-]+\.json", filename):
            return "Error: Invalid filename. Use only letters, numbers, underscores, hyphens, and end with .json."
        save_path = os.path.join(SAVE_DIR, filename)
        game_state = {
            "player": asdict(self.player),
            "current_room": self.current_room,
            # Potentially add other game state aspects here if needed in the future
        }
        try:
            with open(save_path, "w") as f:
                json.dump(game_state, f, indent=4)
            return f"Game saved successfully to {filename}."
        except IOError as e:
            return f"Error saving game: {e}"
        except Exception as e:
            return f"An unexpected error occurred while saving: {e}"

    def load_game(self, filename: str) -> str:
        """Loads the game state from a JSON file."""
        save_path = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(save_path):
            return f"Error: Save file '{filename}' not found."

        try:
            with open(save_path, "r") as f:
                game_state = json.load(f)

            # Restore player state
            player_data = game_state.get("player")
            if not isinstance(player_data, dict):
                return "Error: Invalid save file format (player data missing or malformed)."

            self.player.health = player_data.get("health", self.player.health)
            self.player.energy = player_data.get("energy", self.player.energy)
            self.player.level = player_data.get("level", self.player.level)
            self.player.exp = player_data.get("exp", self.player.exp)
            self.player.inventory = player_data.get("inventory", self.player.inventory)
            self.player.character_class = player_data.get(
                "character_class", self.player.character_class
            )

            # Restore current room
            current_room_data = game_state.get("current_room")
            if (
                not isinstance(current_room_data, str)
                or current_room_data not in self.rooms
            ):
                # Fallback to start room if loaded room is invalid, or handle as error
                # For now, let's be strict and consider it an error.
                return "Error: Invalid save file format (current_room data missing, malformed, or invalid)."
            self.current_room = current_room_data

            return f"Game loaded successfully from {filename}.\n\n{self.rooms[self.current_room].description}"

        except IOError as e:
            return f"Error loading game: {e}"
        except json.JSONDecodeError:
            return "Error: Save file is corrupted or not valid JSON."
        except KeyError as e:
            return f"Error: Save file is missing expected data: {e}."
        except Exception as e:
            return f"An unexpected error occurred while loading: {e}"
