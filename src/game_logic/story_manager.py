from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Character:
    """Player character data structure."""
    char_class: str
    health: int = 100
    max_health: int = 100
    energy: int = 100
    level: int = 1
    exp: int = 0
    inventory: List[str] = field(default_factory=list)

    def __post_init__(self):
        # Set class-specific stats
        if self.char_class == "cybernetic":
            self.strength = 15
            self.tech = 12
            self.agility = 8
            self.special_ability = "shield_matrix"
        elif self.char_class == "psionic":
            self.strength = 6
            self.tech = 10
            self.agility = 12
            self.special_ability = "mind_blast"
        elif self.char_class == "hunter":
            self.strength = 10
            self.tech = 8
            self.agility = 15
            self.special_ability = "stealth_field"

@dataclass
class Room:
    """Game room data structure."""
    name: str
    description: str
    exits: Dict[str, str]
    items: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    requires_key: bool = False
    is_dark: bool = False

class StoryManager:
    """Manages game state and story progression."""

    def __init__(self):
        self.current_room = "cargo_hold"
        self.player: Optional[Character] = None
        self.game_state = "character_creation"
        self.initialize_rooms()

    def initialize_rooms(self):
        """Initialize game rooms and their connections."""
        self.rooms = {
            "cargo_hold": Room(
                name="Abandoned Cargo Hold",
                description="A vast chamber filled with forgotten cargo containers. Emergency lights cast long shadows "
                           "between the towering stacks. The air is thick with the smell of rust and ozone.",
                exits={"north": "maintenance_corridor", "east": "power_junction"},
                items=["medkit"],
                enemies=["corrupted_drone"]
            ),
            "maintenance_corridor": Room(
                name="Maintenance Corridor",
                description="A narrow corridor lined with exposed pipes and damaged control panels. "
                           "Strange whispers seem to echo from the ventilation system.",
                exits={"south": "cargo_hold", "west": "bio_lab"},
                items=["energy_cell"],
                is_dark=True
            ),
            "power_junction": Room(
                name="Power Junction",
                description="A circular room dominated by a crackling energy core. Arcs of electricity "
                           "jump between damaged conduits, creating an ever-shifting dance of light and shadow.",
                exits={"west": "cargo_hold", "north": "psi_chamber"},
                items=["power_cell"],
                enemies=["rogue_bot"]
            ),
            "bio_lab": Room(
                name="Abandoned Bio Lab",
                description="A research lab in disarray. Shattered stasis tubes line the walls, their contents long gone. "
                           "Holographic warnings flicker weakly in the darkness.",
                exits={"east": "maintenance_corridor"},
                items=["health_boost", "research_data"],
                requires_key=True
            ),
            "psi_chamber": Room(
                name="Psi Amplification Chamber",
                description="A mysterious chamber filled with crystalline structures that pulse with inner light. "
                           "The air itself seems to vibrate with psychic energy.",
                exits={"south": "power_junction"},
                items=["psi_shard"],
                enemies=["shadow_entity"]
            )
        }

    def get_opening_text(self) -> str:
        """Get the game's opening text."""
        return """Welcome to Dark Station Chronicles

Choose your class to begin:

CYBERNETIC
Enhanced humans with integrated tech and defensive capabilities.
Special: Integrated shield system and enhanced strength.

PSIONIC
Psychically augmented individuals who can manipulate energy and minds.
Special: Psychic abilities and energy manipulation.

HUNTER
Stealthy operatives with advanced camouflage and targeting systems.
Special: Stealth field generator and enhanced accuracy.

Type 'choose [class]' to begin (e.g., 'choose cybernetic')"""

    def process_command(self, command: str) -> str:
        """Process player commands and return response."""
        command = command.lower().strip()

        # Handle character creation
        if self.game_state == "character_creation":
            return self._handle_character_creation(command)

        # Handle game commands
        if command == "look":
            return self._handle_look_command()
        elif command == "status":
            return self._handle_status_command()
        elif command.startswith("go "):
            return self._handle_movement_command(command[3:])
        elif command == "help":
            return self._handle_help_command()

        return "I don't understand that command. Type 'help' for available commands."

    def _handle_character_creation(self, command: str) -> str:
        """Handle character creation commands."""
        if not command.startswith("choose "):
            return "Please choose your class: cybernetic, psionic, or hunter"

        char_class = command.split()[1]
        if char_class not in ["cybernetic", "psionic", "hunter"]:
            return "Invalid class. Choose cybernetic, psionic, or hunter."

        self.player = Character(char_class)
        self.game_state = "playing"
        return f"You have chosen the {char_class} class. Your journey begins...\n\n{self._get_room_description()}"

    def _handle_look_command(self) -> str:
        """Handle the look command."""
        return self._get_room_description()

    def _handle_status_command(self) -> str:
        """Handle the status command."""
        if not self.player:
            return "No character created yet."
        return (f"Health: {self.player.health}/{self.player.max_health}\n"
                f"Energy: {self.player.energy}\n"
                f"Level: {self.player.level} (EXP: {self.player.exp})\n"
                f"Class: {self.player.char_class}\n"
                f"Special Ability: {self.player.special_ability}")

    def _handle_movement_command(self, direction: str) -> str:
        """Handle movement commands."""
        current_room = self.rooms[self.current_room]
        if direction in current_room.exits:
            next_room_id = current_room.exits[direction]
            next_room = self.rooms[next_room_id]

            if next_room.requires_key and "keycard" not in self.player.inventory:
                return "This door requires a keycard to open."

            if next_room.is_dark and "light_source" not in self.player.inventory:
                return "It's too dark to enter without a light source."

            self.current_room = next_room_id
            return f"You move {direction}.\n\n{self._get_room_description()}"
        return f"You cannot go {direction} from here."

    def _handle_help_command(self) -> str:
        """Handle the help command."""
        return """Available commands:
- look : Look around the room
- status : Check your character's status
- go [direction] : Move in a direction (north, south, east, west)
- help : Show this help message"""

    def _get_room_description(self) -> str:
        """Get the current room's full description."""
        room = self.rooms[self.current_room]
        exits_str = ", ".join(room.exits.keys())
        items_str = ", ".join(room.items) if room.items else "nothing"

        description = f"{room.description}\n\nExits: {exits_str}\nItems: {items_str}"

        if room.enemies:
            enemies_str = ", ".join(room.enemies)
            description += f"\nEnemies present: {enemies_str}"

        return description
