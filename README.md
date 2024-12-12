# Dark-Station-Chronicles
A text-based sci-fi RPG with AI-powered narratives and modular UI.
=======
# Dark Station Chronicles

A text-based sci-fi RPG with AI-powered narrative responses and a modern, modular web interface. Features both cloud-based (Claude) and local (Llama) AI integration.

## Project Structure

```
Game/
├── src/
│   ├── api/
│   │   └── main.py           # FastAPI backend server
│   ├── game_logic/
│   │   └── story_manager.py  # Core game mechanics and state
│   ├── ai/
│   │   └── ai_manager.py     # Multi-model AI integration
│   └── frontend/
│       └── src/
│           ├── components/
│           │   ├── GameInterface.jsx   # Main container component
│           │   ├── StatsPanel.jsx      # Player stats display
│           │   ├── ModelSelector.jsx   # AI model switching UI
│           │   ├── MessageList.jsx     # Game messages display
│           └── App.jsx       # Root React component
├── models/                   # Local AI models directory
├── setup.py                  # Project setup script
├── start-game.sh             # Launch script
└── .env                      # Environment variables
```

## Core Components

### Backend Components

1. **AI Manager** (`src/ai/ai_manager.py`)
   - Dual AI model support:
     - Cloud-based Claude API integration
     - Local Llama.cpp model with GPU acceleration
   - Dynamic model switching
   - Fallback mechanisms
   - Context-aware responses

2. **Story Manager** (`src/game_logic/story_manager.py`)
   - Core game logic and state management
   - Character system (classes, stats, inventory)
   - Room system and navigation
   - Command processing

3. **API Server** (`src/api/main.py`)
   - FastAPI endpoints for game interaction
   - Model switching support
   - State management
   - Command processing with AI integration

### Frontend Components

1. **GameInterface** (`frontend/src/components/GameInterface.jsx`)
   - Main container for the game interface.
   - Orchestrates subcomponents like `StatsPanel`, `ModelSelector`, and `MessageList`.
   - Manages state and handles player input.

2. **StatsPanel** (`frontend/src/components/StatsPanel.jsx`)
   - Displays player stats such as health, energy, and level.
   - Utilizes icons and dynamic progress bars for a polished look.

3. **ModelSelector** (`frontend/src/components/ModelSelector.jsx`)
   - Handles AI model selection and status updates.
   - Provides visual feedback for active/switching models.

4. **MessageList** (`frontend/src/components/MessageList.jsx`)
   - Displays player and system messages.
   - Ensures automatic scrolling for new messages.

## Setup and Requirements

### Initial Setup
```bash
python setup.py
```
This will:
- Create directory structure
- Set up a virtual environment
- Install dependencies
- Configure the frontend

### Environment Configuration
Create a `.env` file with:
```
ANTHROPIC_API_KEY=your_api_key_here
LLAMA_MODEL_PATH=/path/to/your/model.gguf
```

### Model Setup

1. **Claude Setup**
   - Obtain API key from Anthropic.
   - Add it to the `.env` file.

2. **Llama Setup**
   - Download a GGUF model file (e.g., `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`).
   - Place it in the `models/` directory.
   - Update `LLAMA_MODEL_PATH` in the `.env` file.

3. **GPU Acceleration (ROCm for AMD)**
```bash
# Install with ROCm support
CMAKE_ARGS="-DLLAMA_ROCM=ON" pip install llama-cpp-python --no-cache-dir
```

## Running the Game

1. Start the servers:
```bash
./start-game.sh
```
This will:
- Start the backend server
- Launch the frontend
- Open the game in your browser
- Manage logs and cleanup

2. Access the game at: http://localhost:5173

## Features and Capabilities

### AI Integration
- Dual model support (Claude and Llama).
- Dynamic model switching with real-time feedback.
- GPU acceleration for local models.
- Context-aware responses with fallback mechanisms.

### UI Features
- Modular and responsive design.
- Key components:
  - `StatsPanel`: Displays player stats dynamically.
  - `ModelSelector`: Enables seamless switching between AI models.
  - `MessageList`: Handles player and system messages with auto-scrolling.
- Dark theme with consistent and accessible styling.
- Real-time feedback for commands and loading states.

### Game Systems
- Character classes and stats.
- Inventory system.
- Room navigation and exploration.
- Command processing.

## Development and Customization

### Adding New AI Models
1. Create a new backend class in `ai_manager.py`:
```python
class NewModelBackend(AIModelBackend):
    def generate_response(self, prompt: str) -> str:
        # Implementation
```

2. Register in `AIManager.__init__`:
```python
self.backends["new_model"] = NewModelBackend()
```

### UI Customization
1. Add new components to `GameInterface.jsx`:
   - Use the modular structure to integrate additional panels or features.

2. Update styles:
   - Modify `index.css` or component-level styles for Tailwind customization.

### Debugging and Testing
1. Use browser developer tools to inspect UI and API calls.
2. Monitor logs for backend errors.

## Future Improvements

1. **Expanded AI Integration**:
   - Add support for more open-source models like Hugging Face transformers.
   - Introduce multi-prompt or memory-based storytelling.

2. **Enhanced UI/UX**:
   - Add animations for better transitions.
   - Include tooltips and accessibility improvements.

3. **Save/Load System**:
   - Implement JSON-based game state saving and loading.

4. **Procedural Content Generation**:
   - Use AI for dynamic room descriptions and NPC dialogue.

5. **Community Features**:
   - Allow players to create and share custom story modules.

## License

[Add your chosen license here]
