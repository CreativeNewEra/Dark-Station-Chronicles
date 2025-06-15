# Dark Station Chronicles

A text-based sci-fi RPG with AI-powered narrative responses and a modern, modular web interface. Features both cloud-based (Claude) and local (Llama) AI integration.

## Features

### Core Game Features
- Character class system with unique abilities:
  - Cybernetic: Tech-focused with hacking abilities
  - Psionic: Psychic powers and enhanced perception
  - Hunter: Survival and combat specialist
- Room-based exploration system
- Dynamic game state management
- Inventory system
- Health and energy tracking

### AI Integration
- Cloud-based Claude AI support
- Local Llama model support (optional)
- Contextual responses based on:
  - Character class
  - Current location
  - Game state
  - Conversation history
- Seamless model switching
- Fallback mechanisms for reliability

### Modern UI Features
- TypeScript-powered components
- Real-time response formatting with Markdown
- Dynamic stats display
- Smooth transitions and animations
- Model status indicators
- Responsive design

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
│           │   ├── GameInterface.tsx   # Main game container
│           │   ├── StatsPanel.tsx      # Player stats display
│           │   ├── ModelSelector.tsx   # AI model switching
│           │   ├── MessageList.tsx     # Game messages
│           └── App.tsx       # Root React component
├── models/                   # Local AI models directory
├── setup.py                  # Project setup script
├── start-game.sh            # Launch script
└── .env                     # Environment variables
```

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
LLAMA_MODEL_PATH=/path/to/your/model.gguf  # Optional
```

### Model Setup

1. **Claude Setup**
   - Obtain API key from Anthropic
   - Add it to the `.env` file

2. **Llama Setup (Optional)**
   - Download a GGUF model file
   - Place it in the `models/` directory
   - Update `LLAMA_MODEL_PATH` in `.env`

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

## Development

### Key Components

1. **AI Manager** (`src/ai/ai_manager.py`)
   - Handles AI model integration
   - Manages conversation history
   - Provides context-aware responses
   - Implements fallback mechanisms

2. **Story Manager** (`src/game_logic/story_manager.py`)
   - Manages game state
   - Handles character classes
   - Controls room navigation
   - Processes game commands

3. **Frontend Components**
   - TypeScript-based React components
   - Real-time updates
   - Responsive design
   - Markdown formatting support

### Adding New Features

1. **New AI Models**
```python
class NewModelBackend(AIModelBackend):
    def generate_response(self, prompt: str) -> str:
        # Implementation
```

2. **New Character Classes**
   - Add class definition to story_manager.py
   - Update AI prompts in ai_manager.py
   - Add UI elements in frontend

## Future Improvements

1. **Enhanced Game Mechanics**
   - Combat system
   - Item crafting
   - NPC interactions
   - Quest system

2. **AI Enhancements**
   - More detailed memory system
   - Dynamic story generation
   - Adaptive difficulty

3. **UI Improvements**
   - Mini-map system
   - Sound effects
   - Inventory visualization
   - Character customization interface

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
