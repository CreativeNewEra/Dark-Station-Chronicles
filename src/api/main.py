import logging
import os
import datetime  # Added for timestamping save files
import uuid
from dotenv import load_dotenv
from typing import Optional, Dict, List, Literal, Any  # Added Any

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env if available
load_dotenv()


# --- Model classes ---


class SwitchModelRequest(BaseModel):
    model: Literal[
        "claude",
        "llama",
        "openai",
        "gemini",
        "openrouter",
    ]


class GameCommand(BaseModel):
    command: str
    use_ai: bool = False
    model: Literal[
        "claude",
        "llama",
        "openai",
        "gemini",
        "openrouter",
    ] = "claude"


class GameState(BaseModel):
    current_room: str
    player_stats: Dict[str, Any]  # Changed to 'Any' for flexibility
    inventory: List[str]
    available_exits: List[str]
    character_class: Optional[str] = None


class GameResponse(BaseModel):
    message: str
    game_state: Optional[GameState] = None


class SaveGameRequest(BaseModel):
    filename: Optional[str] = None  # Filename is now optional


class LoadGameRequest(BaseModel):
    filename: str


class SaveFile(BaseModel):
    filename: str
    timestamp: str  # Or datetime object, depending on preference


# --- Import managers ---
try:
    from src.game_logic.story_manager import StoryManager, SAVE_DIR
    from src.ai.ai_manager import AIManager
except Exception as e:
    logger.error(f"Error importing managers: {e}")
    raise


# Initialize FastAPI app
app = FastAPI(title="Dark Station Chronicles API")

# Configure CORS
origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory session store with TTL
sessions: Dict[str, Dict[str, Any]] = (
    {}
)  # Stores {'manager': StoryManager, 'last_access': datetime}
SESSION_TTL_SECONDS = int(
    os.getenv("SESSION_TTL_SECONDS", "3600")
)  # Default TTL is 1 hour


# Dependency providers
def get_story_manager(request: Request, response: Response) -> StoryManager:
    """Retrieve or create a StoryManager tied to a session."""
    try:
        session_id = request.cookies.get("session-id")
        if session_id and session_id in sessions:
            return sessions[session_id]

        story_manager = StoryManager()
        session_id = str(uuid.uuid4())
        sessions[session_id] = story_manager
        cookie_secure = os.getenv("COOKIE_SECURE", "True").lower() == "true"
        response.set_cookie(
            "session-id", session_id, httponly=True, secure=cookie_secure, samesite="Lax"
        )
        return story_manager
    except Exception as e:
        logger.error(f"Error creating StoryManager: {e}")
        raise


def get_ai_manager() -> AIManager:
    """Create a new AIManager for each request."""
    try:
        return AIManager()
    except Exception as e:
        logger.error(f"Error creating AIManager: {e}")
        raise


# --- Helper function to get current game state ---
def get_game_state_details(story_manager: StoryManager) -> Optional[GameState]:
    """Helper function to get current game state details"""
    try:
        if not story_manager.player:
            logger.warning(
                "Attempted to get game state, but story_manager.player is not initialized."
            )
            return None

        current_room_details = story_manager.rooms.get(story_manager.current_room)
        if not current_room_details:
            logger.error(
                f"Current room '{story_manager.current_room}' not found in story_manager.rooms."
            )
            return None  # Or raise an error, or default to a start room state

        return GameState(
            current_room=story_manager.current_room,
            player_stats={
                "health": story_manager.player.health,
                "energy": story_manager.player.energy,
                "level": story_manager.player.level,
                "exp": story_manager.player.exp,
            },
            inventory=story_manager.player.inventory,
            available_exits=list(current_room_details.exits.keys()),
            character_class=story_manager.player.character_class,
        )
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        logger.exception("Full traceback for get_game_state_details:")
        return None


# --- API Endpoints ---


@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"status": "online", "game": "Dark Station Chronicles"}


@app.post("/game/command", response_model=GameResponse)
async def process_command_endpoint(
    command: GameCommand,
    story_manager: StoryManager = Depends(get_story_manager),
    ai_manager: AIManager = Depends(get_ai_manager),
):
    """Process a game command"""
    try:
        logger.info(
            f"Processing command: {command.command} with AI: {command.use_ai}, Model: {command.model}"
        )

        response_text = story_manager.process_command(command.command)
        logger.info(f"Story manager response: {response_text}")

        if command.use_ai:
            try:
                current_game_state = get_game_state_details(story_manager)
                state_dict_for_ai = (
                    current_game_state.dict() if current_game_state else {}
                )

                if command.model != ai_manager.current_backend:
                    if not ai_manager.switch_backend(command.model):
                        logger.error(f"Failed to switch AI model to {command.model}")
                        # Not raising HTTPException here to allow base game response
                        response_text += (
                            f"\n\n(Note: Could not switch to AI model {command.model}.)"
                        )
                    else:
                        logger.info(
                            f"Successfully switched AI model to {command.model}"
                        )

                ai_response = ai_manager.get_ai_response(
                    command.command, state_dict_for_ai
                )
                response_text = f"{response_text}\n\n{ai_response}"
            except Exception as ai_error:
                logger.error(f"AI enhancement failed: {ai_error}")
                response_text += "\n\n(AI enhancement encountered an error.)"

        return GameResponse(
            message=response_text,
            game_state=get_game_state_details(story_manager),
        )

    except Exception as e:
        logger.error(f"Error processing command: {e}")
        logger.exception("Full traceback for process_command_endpoint:")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/game/start", response_model=GameResponse)
async def start_game_endpoint(
    story_manager: StoryManager = Depends(get_story_manager),
):
    """Initialize a new game session or get opening text"""
    try:
        # Re-initialize story_manager for a fresh game start if desired,
        # or ensure it's in a clean state. For now, just gets opening text.
        # story_manager.__init__() # Uncomment if a full reset is needed on /game/start
        opening_text = story_manager.get_opening_text()
        return GameResponse(
            message=opening_text,
            game_state=get_game_state_details(story_manager),
        )
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/game/switch-model")
async def switch_model_endpoint(
    request: SwitchModelRequest,
    ai_manager: AIManager = Depends(get_ai_manager),
):
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


@app.get("/game/state", response_model=Optional[GameState])
async def get_current_state_endpoint(
    story_manager: StoryManager = Depends(get_story_manager),
):
    """Get current game state"""
    try:
        state = get_game_state_details(story_manager)
        if not state:
            # It's possible a game hasn't started or an error occurred.
            # Depending on desired behavior, could return 404 or an empty/default state.
            logger.info(
                "No active game session or error retrieving state for /game/state."
            )
            # Return None or an empty GameState if that's more appropriate than 404
            # For now, let's allow None to be returned by the response_model
            return None
        return state
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Save/Load Endpoints ---


@app.post("/game/save", response_model=GameResponse)
async def save_game_endpoint(
    request: SaveGameRequest,
    story_manager: StoryManager = Depends(get_story_manager),
):
    """Saves the current game state."""
    try:
        filename = request.filename
        if not filename:
            # Generate a filename with a timestamp if not provided
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"savegame_{timestamp}.json"
        else:
            # Ensure filename ends with .json
            if not filename.endswith(".json"):
                filename += ".json"

        message = story_manager.save_game(filename)
        if "Error" in message:
            raise HTTPException(status_code=500, detail=message)
        return GameResponse(
            message=message,
            game_state=get_game_state_details(story_manager),
        )
    except HTTPException:
        raise  # Re-raise HTTPException to preserve status code and detail
    except Exception as e:
        logger.error(f"Error in save_game_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save game: {str(e)}")


@app.post("/game/load", response_model=GameResponse)
async def load_game_endpoint(
    request: LoadGameRequest,
    story_manager: StoryManager = Depends(get_story_manager),
):
    """Loads a game state from a file."""
    try:
        filename = request.filename
        if not filename.endswith(".json"):  # Ensure consistency
            filename += ".json"
        message = story_manager.load_game(filename)
        if "Error" in message:  # Check for errors from story_manager.load_game
            # Distinguish between file not found and other errors
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message)
            raise HTTPException(
                status_code=400, detail=message
            )  # Bad request if file is corrupted etc.
        return GameResponse(
            message=message,
            game_state=get_game_state_details(story_manager),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in load_game_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load game: {str(e)}")


@app.get("/game/saves", response_model=List[SaveFile])
async def list_save_files_endpoint():
    """Lists available save files."""
    try:
        if not os.path.exists(SAVE_DIR):
            # If SAVE_DIR doesn't exist (e.g. StoryManager failed to create it), return empty list
            return []

        saves = []
        for f_name in os.listdir(SAVE_DIR):
            if f_name.endswith(".json"):
                file_path = os.path.join(SAVE_DIR, f_name)
                try:
                    # Get last modified timestamp
                    timestamp_epoch = os.path.getmtime(file_path)
                    timestamp_readable = datetime.datetime.fromtimestamp(
                        timestamp_epoch
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    saves.append(
                        SaveFile(filename=f_name, timestamp=timestamp_readable)
                    )
                except Exception as e:
                    logger.error(f"Could not process save file {f_name}: {e}")
                    # Optionally skip this file or add with a default/error timestamp
                    saves.append(SaveFile(filename=f_name, timestamp="Unknown"))

        # Sort saves by timestamp, most recent first
        saves.sort(key=lambda x: x.timestamp, reverse=True)
        return saves
    except Exception as e:
        logger.error(f"Error listing save files: {e}")
        raise HTTPException(status_code=500, detail="Failed to list save files.")


if __name__ == "__main__":
    import uvicorn

    # Ensure SAVE_DIR exists at startup when running directly
    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            logger.info(f"Created save directory: {os.path.abspath(SAVE_DIR)}")
        except Exception as e:
            logger.error(f"Could not create save directory {SAVE_DIR}: {e}")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
