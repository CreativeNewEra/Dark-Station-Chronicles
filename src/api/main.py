import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Literal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env if available
load_dotenv()


# Model classes
class SwitchModelRequest(BaseModel):
    model: Literal["claude", "llama"]


class GameCommand(BaseModel):
    command: str
    use_ai: bool = False
    model: Literal["claude", "llama"] = "claude"


class GameState(BaseModel):
    current_room: str
    player_stats: Dict[str, int]
    inventory: List[str]
    available_exits: List[str]


class GameResponse(BaseModel):
    message: str
    game_state: Optional[GameState] = None


# Import managers
try:
    from src.game_logic.story_manager import StoryManager
    from src.ai.ai_manager import AIManager
except Exception as e:
    logger.error(f"Error importing managers: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(title="Dark Station Chronicles API")

# Configure CORS
# Allow origins can be provided as a comma-separated list via CORS_ORIGINS
# environment variable. Defaults to localhost dev server.
origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173")
allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
try:
    story_manager = StoryManager()
    ai_manager = AIManager()
except Exception as e:
    logger.error(f"Error initializing managers: {e}")
    raise


def get_game_state() -> Optional[GameState]:
    """Helper function to get current game state"""
    try:
        if not story_manager.player:
            return None

        current_room = story_manager.rooms[story_manager.current_room]
        return GameState(
            current_room=story_manager.current_room,
            player_stats={
                "health": story_manager.player.health,
                "energy": story_manager.player.energy,
                "level": story_manager.player.level,
            },
            inventory=story_manager.player.inventory,
            available_exits=list(current_room.exits.keys()),
        )
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        return None


@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"status": "online", "game": "Dark Station Chronicles"}


@app.post("/game/command")
async def process_command(command: GameCommand) -> GameResponse:
    """Process a game command"""
    try:
        logger.info(f"Processing command: {command.command}")

        # Get base game response
        response = story_manager.process_command(command.command)
        logger.info(f"Story manager response: {response}")

        # If AI is enabled, enhance the response
        if command.use_ai:
            try:
                game_state = get_game_state()
                state_dict = game_state.dict() if game_state else {}

                if command.model != ai_manager.current_backend:
                    if not ai_manager.switch_backend(command.model):
                        raise HTTPException(
                            status_code=500,
                            detail=f"Model {command.model} unavailable",
                        )

                ai_response = ai_manager.get_ai_response(command.command, state_dict)
                response = f"{response}\n\n{ai_response}"
            except Exception as ai_error:
                logger.error(f"AI enhancement failed: {ai_error}")
                # Continue with base response if AI fails

        return GameResponse(message=response, game_state=get_game_state())

    except Exception as e:
        logger.error(f"Error processing command: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/start")
async def start_game():
    """Initialize a new game session"""
    try:
        opening_text = story_manager.get_opening_text()
        return GameResponse(message=opening_text)
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/switch-model")
async def switch_model(request: SwitchModelRequest):
    """Switch between AI models"""
    try:
        success = ai_manager.switch_backend(request.model)
        if not success:
            raise HTTPException(
                status_code=500, detail=f"Failed to switch to {request.model}"
            )
        return {"message": f"Successfully switched to {request.model}"}
    except Exception as e:
        logger.error(f"Error switching model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/game/state")
async def get_current_state():
    """Get current game state"""
    try:
        state = get_game_state()
        if not state:
            raise HTTPException(status_code=404, detail="No active game session")
        return state
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
