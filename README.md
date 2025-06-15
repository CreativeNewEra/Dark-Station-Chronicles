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
- OpenAI API support
- Google Gemini API support
- OpenRouter API support
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
└── .env.template           # Example environment file
```

## Setup and Requirements

### Prerequisites
Ensure you have Python 3.11+ and Node.js with npm installed. The exact commands
depend on your operating system:

- **Fedora (dnf)**: `sudo dnf install nodejs npm`
- **Debian/Ubuntu (apt)**: `sudo apt update && sudo apt install nodejs npm`
- **macOS (Homebrew)**: `brew install node`

If your system uses another package manager, install Node.js and npm manually.
The setup script will exit if they are missing.

### Initial Setup
```bash
python setup.py
```
This will:
- Create directory structure
- Set up a virtual environment
- Install Python dependencies
- Configure the frontend

### Environment Configuration
Copy `.env.template` to `.env` and add your settings:
```
ANTHROPIC_API_KEY=your_api_key_here
LLAMA_MODEL_PATH=/path/to/your/model.gguf  # Optional
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
CORS_ORIGINS=http://localhost:5173  # Allowed origins for CORS
```

### Model Setup

1. **Claude Setup**
   - Obtain API key from Anthropic
   - Add it to your `.env` file

2. **Llama Setup (Optional)**
   - Download a GGUF model file
   - Place it in the `models/` directory
   - Update `LLAMA_MODEL_PATH` in your `.env` file

3. **OpenAI Setup**
   - Obtain API key from OpenAI
   - Add `OPENAI_API_KEY` to your `.env` file

4. **Gemini Setup**
   - Obtain API key for Google Gemini
   - Add `GEMINI_API_KEY` to your `.env` file

5. **OpenRouter Setup**
   - Obtain API key from OpenRouter
   - Add `OPENROUTER_API_KEY` to your `.env` file

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

Alternatively, to run only the backend during development, execute:

```bash
python -m uvicorn src.api.main:app --reload
```
Run this from the project root so package imports resolve correctly.

2. Access the game at: http://localhost:5173

## Docker Usage

You can also run the project using Docker. Build the containers and start both
services with `docker compose`:

```bash
docker compose build
docker compose up
```

The backend API will be available on `http://localhost:8000` and the frontend on
`http://localhost:5173`. Ensure you have a `.env` file in the project root so
the backend container can read your API keys.

## Development

### Pre-commit Hooks

Set up Git hooks to automatically lint and format your code:

```bash
pip install pre-commit
pre-commit install
```

This config runs `black`, `flake8`, and `eslint` on each commit.

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
