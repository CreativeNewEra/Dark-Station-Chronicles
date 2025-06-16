# Dark Station Chronicles - Agent Documentation

**Created**: June 15, 2025  
**Version**: 1.0  
**Target Audience**: AI Agents and Development Tools

---

## Project Overview

Dark Station Chronicles is a sophisticated text-based sci-fi RPG that combines modern web technologies with AI-powered narrative generation. The game features a modular architecture with both cloud-based (Claude) and local (Llama) AI integration, providing players with immersive, context-aware storytelling experiences.

### Core Concept

Players explore a mysterious space station through text-based commands, with AI generating dynamic responses based on character class, location, game state, and conversation history. The game emphasizes emergent storytelling and player agency within a sci-fi setting.

## Quick Start Guide

For AI agents working with this project for the first time:

1. **Understand the Architecture**: This is a dual-stack application (Python FastAPI + React TypeScript)
2. **Check Dependencies**: Ensure Python 3.11+, Node.js, and npm are available
3. **Environment Setup**: Copy `.env.template` to `.env` and configure API keys
4. **Run Setup**: Execute `python setup.py` for automated configuration
5. **Start Development**: Use `./start-game.sh` to launch both frontend and backend
6. **Access Game**: Navigate to `http://localhost:5173` to interact with the game

### Key Files to Understand

- `src/api/main.py`: FastAPI routes and request handling
- `src/ai/ai_manager.py`: AI model abstraction and management
- `src/game_logic/story_manager.py`: Core game mechanics and state
- `frontend/src/components/GameInterface.tsx`: Main UI component
- `requirements.txt`: Python dependencies
- `frontend/package.json`: Node.js dependencies

## Architecture Overview

### Technology Stack

#### Backend (Python)

- FastAPI for REST API endpoints
- Python 3.11+ with async/await support
- Pydantic for data validation
- Anthropic Claude API integration
- Optional Llama.cpp for local AI models
- Environment-based configuration

#### Frontend (TypeScript/React)

- React 18.3+ with hooks and TypeScript
- Vite for build tooling and development server
- Tailwind CSS for styling with typography plugin
- React Markdown for rich text rendering
- Lucide React for icons
- Real-time WebSocket-like communication via REST

#### Infrastructure

- Docker containerization with multi-service compose
- Environment variable configuration
- CORS handling for cross-origin requests
- Logging and error handling

## Project Structure

```text
/home/ant/AI/Dark-Station-Chronicles/
├── src/                          # Python backend source
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI application and routes
│   ├── ai/
│   │   ├── __init__.py
│   │   └── ai_manager.py        # AI model abstraction and management
│   └── game_logic/
│       ├── __init__.py
│       └── story_manager.py     # Game state and mechanics
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── GameInterface.tsx    # Main game container
│   │   │   ├── StatsPanel.tsx       # Player stats display
│   │   │   ├── ModelSelector.tsx    # AI model switching UI
│   │   │   └── MessageList.tsx      # Game message history
│   │   ├── types.ts                 # TypeScript type definitions
│   │   ├── App.jsx                  # Root component
│   │   └── main.jsx                 # React entry point
│   ├── public/                      # Static assets
│   ├── package.json                 # Frontend dependencies
│   └── vite.config.js              # Vite configuration
├── models/                          # Local AI models directory
├── requirements.txt                 # Python dependencies
├── package.json                     # Root project linting
├── docker-compose.yml              # Multi-service container setup
├── Dockerfile.backend              # Backend container config
├── Dockerfile.frontend             # Frontend container config
├── setup.py                        # Automated project setup
├── start-game.sh                   # Development launch script
└── .env.template                   # Environment variables template
```

## Key Components

### 1. AI Manager (`src/ai/ai_manager.py`)

**Purpose**: Provides abstraction layer for multiple AI models with consistent interface.

**Key Classes**:

- `AIModelBackend`: Abstract base class for AI implementations
- `ClaudeBackend`: Anthropic Claude API integration
- `LlamaBackend`: Local Llama model support
- `AIManager`: Main manager class with conversation history

**Features**:

- Context-aware prompt generation
- Conversation history management
- Model switching capabilities
- Fallback mechanisms for reliability
- Character class-specific prompting

**Usage Pattern**:

```python
ai_manager = AIManager()
response = ai_manager.generate_response(
    command="look around",
    character_class="cybernetic",
    current_room="lab",
    game_state=game_state
)
```

### 2. Story Manager (`src/game_logic/story_manager.py`)

**Purpose**: Handles core game mechanics, state management, and world simulation.

**Key Classes**:

- `Player`: Player stats, inventory, and character class
- `Room`: Room descriptions and navigation
- `StoryManager`: Main game logic controller

**Features**:

- Character class system (Cybernetic, Psionic, Hunter)
- Room-based exploration
- Inventory management
- Health/energy tracking
- Command processing and validation

**Character Classes**:

- **Cybernetic**: Tech-focused, hacking abilities, enhanced with implants
- **Psionic**: Psychic powers, enhanced perception, mental abilities
- **Hunter**: Survival specialist, combat expertise, tracking skills

### 3. API Layer (`src/api/main.py`)

**Purpose**: FastAPI backend providing REST endpoints for game interaction.

**Key Endpoints**:

- `POST /start_game`: Initialize new game session
- `POST /process_command`: Handle player commands
- `POST /switch_model`: Change AI model
- `GET /game_state`: Retrieve current game state
- `GET /health`: Health check endpoint

**Request/Response Models**:

- `GameCommand`: Player input with AI options
- `GameState`: Complete game state representation
- `SwitchModelRequest`: Model switching requests
- `MODEL_NAMES`: Tuple listing valid AI backend identifiers

### 4. Game Interface (`frontend/src/components/GameInterface.tsx`)

**Purpose**: Main React component orchestrating the game UI.

**Features**:

- Real-time message display with Markdown support
- Command input with history
- Model switching interface
- Loading states and error handling
- Responsive design with Tailwind CSS

**State Management**:

- React hooks for local state
- API communication for game state
- Message history with typing indicators
- Model status tracking

## Game Mechanics

### Character Classes

#### Cybernetic

- Focus: Technology and hacking
- Abilities: Enhanced tech interaction, system access
- Gameplay: Emphasis on electronic warfare and augmentation

#### Psionic

- Focus: Psychic abilities and perception
- Abilities: Mental powers, enhanced awareness
- Gameplay: Psychic exploration and mind-based puzzles

#### Hunter

- Focus: Survival and combat
- Abilities: Tracking, weapon expertise, survival skills
- Gameplay: Combat encounters and environmental challenges

### World Design

#### Setting

Abandoned space station with mysterious circumstances

#### Atmosphere

Sci-fi horror with mystery elements

#### Exploration

Room-based navigation with rich descriptions

#### Narrative

AI-generated responses based on context and character

## Configuration

### Environment Variables

**Required**:

- `ANTHROPIC_API_KEY`: Claude API access key

**Optional**:

- `LLAMA_MODEL_PATH`: Path to local GGUF model file
- `CORS_ORIGINS`: Allowed CORS origins (default: `http://localhost:5173`)

### Model Setup

**Claude (Cloud)**:

1. Obtain API key from Anthropic Console
2. Add to `.env` file
3. Automatic initialization on startup

**Llama (Local)**:

1. Download GGUF format model
2. Place in `models/` directory
3. Update `LLAMA_MODEL_PATH` in `.env`
4. Requires `llama-cpp-python` dependency

## Development Workflow

### Initial Setup

```bash
# Automated setup
python setup.py

# Manual setup alternative
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

### Running Development Server

```bash
# Automated (recommended)
./start-game.sh

# Manual backend only
python -m uvicorn src.api.main:app --reload

# Manual frontend only
cd frontend && npm run dev
```

### Docker Development

```bash
# Build and run all services
docker compose build
docker compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Code Quality

- Pre-commit hooks with Black, Flake8, ESLint
- TypeScript strict mode
- Comprehensive error handling
- Logging throughout application

## API Reference

### Game Commands

**Basic Commands**:

- `look` / `look around`: Examine current room
- `go [direction]`: Move between rooms
- `inventory`: Check player inventory
- `stats`: Display player statistics
- `help`: Show available commands

**AI Integration**:

- Commands can be processed with or without AI
- AI responses are contextual and character-specific
- Model switching available during gameplay

### Data Models

**GameState**:

```typescript
interface GameState {
    current_room: string;
    player: {
        health: number;
        energy: number;
        level: number;
        exp: number;
        inventory: string[];
        character_class: string | null;
    };
    message: string;
    available_commands: string[];
}
```

**Message**:

```typescript
interface Message {
    type: 'user' | 'game' | 'ai' | 'system';
    content: string;
    timestamp: Date;
}
```

## Testing

### Test Files

- `test_ai.py`: AI manager functionality
- `test_enhanced_ai.py`: Enhanced AI features
- `test_story_manager.py`: Game logic testing
- `test_api_endpoints.py`: API endpoint testing

### Test Coverage

- AI model switching and fallbacks
- Game state management
- Command processing
- API endpoint validation

## Deployment Considerations

### Production Setup

- Environment variable security
- API key management
- CORS configuration for production domains
- Docker container optimization
- Logging configuration

### Scaling

- Stateless design enables horizontal scaling
- Database integration for persistent state
- Session management for multiple players
- Rate limiting for API endpoints

## Future Enhancements

### Planned Features

1. **Enhanced Game Mechanics**
   - Combat system with dice rolls
   - Item crafting and equipment
   - NPC interactions and dialogue trees
   - Quest system with objectives

2. **AI Improvements**
   - Enhanced memory and context retention
   - Dynamic story generation
   - Adaptive difficulty based on player choices
   - Multi-model ensemble responses

3. **UI/UX Enhancements**
   - Mini-map visualization
   - Sound effects and ambient audio
   - Character avatar customization
   - Inventory visualization with icons

4. **Technical Improvements**
   - WebSocket real-time communication
   - Database persistence layer
   - User authentication and profiles
   - Save/load game functionality

## Common Issues and Solutions

### AI Model Issues

- **Claude API Limits**: Implement rate limiting and retry logic
- **Llama Performance**: Optimize model size and inference parameters
- **Context Length**: Implement conversation history truncation

### Development Issues

- **CORS Errors**: Verify CORS_ORIGINS configuration
- **Package Conflicts**: Use virtual environments
- **Port Conflicts**: Check for running services on 8000/5173

### Deployment Issues

- **Environment Variables**: Ensure .env file is properly configured
- **Docker Builds**: Clear cache if builds fail
- **Model Loading**: Verify model file paths and permissions

## Troubleshooting Quick Reference

### Common Commands

```bash
# Check if services are running
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port

# Restart services
./start-game.sh

# Manual service restart
python -m uvicorn src.api.main:app --reload  # Backend
cd frontend && npm run dev  # Frontend

# Check logs
tail -f backend.log
tail -f frontend.log

# Dependencies
pip install -r requirements.txt  # Python deps
cd frontend && npm install  # Node deps
```

### Environment Variables Checklist

- [ ] `.env` file exists in project root
- [ ] `ANTHROPIC_API_KEY` is set (required for Claude)
- [ ] `LLAMA_MODEL_PATH` is set (optional, for local AI)
- [ ] `CORS_ORIGINS` matches your frontend URL
- [ ] File permissions are correct for model files

## Contributing Guidelines

### Code Style

- Python: Follow PEP 8, use Black formatter
- TypeScript: ESLint configuration provided
- Comments: Document complex logic and AI prompts
- Commit: Use conventional commit messages

### Testing Requirements

- Write tests for new features
- Maintain test coverage above 80%
- Test AI integrations with mock responses
- Validate API endpoints with various inputs

### Documentation

- Update this agent.md for architectural changes
- Document new API endpoints
- Provide examples for new features
- Update README for user-facing changes

This documentation provides a comprehensive overview for AI agents working with the Dark Station Chronicles project, covering architecture, implementation details, and development workflows.
