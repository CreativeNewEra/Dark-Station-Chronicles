from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Player:
    health: int = 100
    energy: int = 100
    level: int = 1
    exp: int = 0
    inventory: List[str] = None
    character_class: Optional[str] = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

@dataclass
class Room:
    description: str
    exits: Dict[str, str]  # direction -> room_id mapping

class StoryManager:
    def __init__(self):
        self.player = Player()
        self.current_room = "start"

        # Initialize rooms
        self.rooms = {
            "start": Room(
                description="You find yourself in the dimly lit reception area of Dark Station. "
                          "Emergency lights cast an eerie red glow across abandoned terminals.",
                exits={"north": "corridor", "east": "security"}
            ),
            "corridor": Room(
                description="A long corridor stretches before you. Loose cables hang from the ceiling, "
                          "occasionally sparking with residual power.",
                exits={"south": "start", "north": "lab"}
            ),
            "security": Room(
                description="The security office is a mess of broken monitors and scattered datapads. "
                          "A powered-down security robot sits motionless in the corner.",
                exits={"west": "start"}
            ),
            "lab": Room(
                description="This appears to be a research laboratory. Strange equipment lines the walls, "
                          "and holographic displays flicker with corrupted data.",
                exits={"south": "corridor"}
            )
        }

    def get_opening_text(self) -> str:
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
        current_room = self.rooms[self.current_room]
        if direction in current_room.exits:
            self.current_room = current_room.exits[direction]
            return f"You move {direction}.\n\n{self.rooms[self.current_room].description}"
        return f"You cannot go {direction} from here."

    def _handle_examine(self, command: str) -> str:
        target = command[8:].strip()  # Remove "examine " from the start

        # Add some basic examination responses
        if target == "room" or target == "area":
            return self.rooms[self.current_room].description
        elif target == "self":
            return f"Health: {self.player.health}%\nEnergy: {self.player.energy}%\nLevel: {self.player.level}"

        return f"You examine the {target}, but find nothing particularly interesting."

    def _handle_class_selection(self, command: str) -> str:
        class_name = command.split()[-1].lower()
        valid_classes = ["cybernetic", "psionic", "hunter"]

        if class_name in valid_classes:
            self.player.character_class = class_name
            return f"You have chosen the {class_name} class. Your journey begins..."

        return "Invalid class. Choose from: cybernetic, psionic, or hunter."
