import sys
import os
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # Move this up
from typing import Optional, Dict, List, Literal  # Combine all typing imports

# Now we can define the model classes
class SwitchModelRequest(BaseModel):
    model: Literal["claude", "llama"]

# Rest of your imports
from game_logic.story_manager import StoryManager
from ai.ai_manager import AIManager

# Initialize FastAPI app
app = FastAPI(title="Dark Station Chronicles API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
story_manager = StoryManager()
ai_manager = AIManager()

# Pydantic models for request/response validation
class GameState(BaseModel):
    current_room: str
    player_stats: Dict[str, int]
    inventory: List[str]
    available_exits: List[str]

class GameCommand(BaseModel):
    command: str
    use_ai: bool = False
    model: Literal["claude", "llama"] = "claude"

class GameResponse(BaseModel):
    message: str
    game_state: Optional[GameState] = None

def get_game_state() -> Optional[GameState]:
    """Helper function to get current game state"""
    if not story_manager.player:
        return None

    current_room = story_manager.rooms[story_manager.current_room]
    return GameState(
        current_room=story_manager.current_room,
        player_stats={
            "health": story_manager.player.health,
            "energy": story_manager.player.energy,
            "level": story_manager.player.level,
            "exp": story_manager.player.exp
        },
        inventory=story_manager.player.inventory,
        available_exits=list(current_room.exits.keys())
    )

@app.post("/game/switch-model")
async def switch_model(request: SwitchModelRequest):
    """Switch between AI models"""
    try:
        success = ai_manager.switch_backend(request.model)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to switch to {request.model}")
        return {"message": f"Successfully switched to {request.model}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"status": "online", "game": "Dark Station Chronicles"}

@app.get("/game/start")
async def start_game():
    """Initialize a new game session"""
    opening_text = story_manager.get_opening_text()
    return GameResponse(message=opening_text)

@app.post("/game/command")
async def process_command(command: GameCommand) -> GameResponse:
    """Process a game command"""
    try:
        # Get base game response
        response = story_manager.process_command(command.command)

        # If AI is enabled, enhance the response using the selected model
        if command.use_ai:
            game_state = get_game_state()
            state_dict = game_state.dict() if game_state else {}

            # Set the AI model before getting response
            if command.model != ai_manager.current_backend:
                ai_manager.switch_backend(command.model)

            ai_response = ai_manager.get_ai_response(command.command, state_dict)
            response = f"{response}\n\n{ai_response}"

        return GameResponse(
            message=response,
            game_state=get_game_state()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/game/state")
async def get_current_state():
    """Get current game state"""
    state = get_game_state()
    if not state:
        raise HTTPException(status_code=404, detail="No active game session")
    return state

@app.post("/game/reset")
async def reset_game():
    """Reset the game to initial state"""
    global story_manager
    story_manager = StoryManager()
    return GameResponse(message="Game reset. Type 'start' to begin a new game.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
