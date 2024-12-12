from typing import Optional, Dict, Any, Literal, List
from abc import ABC, abstractmethod
import logging
import anthropic
from llama_cpp import Llama
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModelBackend(ABC):
    """Abstract base class for AI model backends"""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate response from the model"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available"""
        pass

class ClaudeBackend(AIModelBackend):
    """Claude API backend"""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = anthropic.Client(api_key=self.api_key)
            logger.info("Successfully initialized Claude backend")
        else:
            self.client = None
            logger.warning("No Anthropic API key found")

    def generate_response(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Claude backend not configured")

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting Claude response: {e}")
            raise

    def is_available(self) -> bool:
        return self.client is not None

class LlamaBackend(AIModelBackend):
    """Local Llama.cpp backend"""

    def __init__(self):
        model_path = os.getenv("LLAMA_MODEL_PATH")
        if model_path and os.path.exists(model_path):
            try:
                self.model = Llama(
    model_path=model_path,
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=32  # This enables GPU acceleration
)
                logger.info("Successfully initialized Llama backend")
            except Exception as e:
                self.model = None
                logger.error(f"Failed to initialize Llama model: {e}")
        else:
            self.model = None
            logger.warning("No Llama model path found or invalid path")

    def generate_response(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Llama backend not configured")

        try:
            response = self.model(
                prompt,
                max_tokens=512,
                temperature=0.7,
                stop=["Human:", "Assistant:"]
            )
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Error getting Llama response: {e}")
            raise

    def is_available(self) -> bool:
        return self.model is not None

class AIManager:
    """Enhanced AI Manager supporting multiple model backends"""

    def __init__(self):
        load_dotenv()

        # Initialize backends
        self.backends = {
            "claude": ClaudeBackend(),
            "llama": LlamaBackend()
        }

        # Set default backend
        self._current_backend = os.getenv("DEFAULT_AI_BACKEND", "claude")

        # Game context for AI responses
        self.game_context = """You are the AI game master for Dark Station Chronicles.
        The game is set in an abandoned space station where players can choose between cybernetic,
        psionic, and hunter classes. Respond in character as an atmospheric, engaging game master."""

    @property
    def current_backend(self) -> str:
        """Get the name of the current backend"""
        return self._current_backend

    @property
    def available_backends(self) -> List[str]:
        """Get list of available backends"""
        return [name for name, backend in self.backends.items()
                if backend.is_available()]

    def switch_backend(self, backend_name: Literal["claude", "llama"]) -> bool:
        """Switch the active AI backend"""
        logger.info(f"Attempting to switch to {backend_name} backend")

        if backend_name not in self.backends:
            logger.error(f"Unknown backend: {backend_name}")
            return False

        if not self.backends[backend_name].is_available():
            logger.error(f"Backend {backend_name} is not available")
            return False

        self._current_backend = backend_name
        logger.info(f"Successfully switched to {backend_name} backend")
        return True

    def get_ai_response(self, prompt: str, game_state: Optional[Dict[str, Any]] = None) -> str:
        """Get AI response using the current backend"""
        try:
            backend = self.backends[self.current_backend]
            if not backend.is_available():
                # Try to fall back to another available backend
                for name, fallback in self.backends.items():
                    if name != self.current_backend and fallback.is_available():
                        logger.info(f"Falling back to {name} backend")
                        backend = fallback
                        break
                else:
                    raise RuntimeError("No AI backends available")

            # Construct the full prompt
            full_prompt = self._construct_prompt(prompt, game_state)

            return backend.generate_response(full_prompt)

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I encountered an error processing your request."

    def _construct_prompt(self, user_input: str, game_state: Optional[Dict[str, Any]] = None) -> str:
        """Construct the full prompt including context and game state"""
        prompt_parts = [self.game_context]

        if game_state:
            state_context = f"""
            Current game state:
            - Location: {game_state.get('current_room', 'unknown')}
            - Player stats: {game_state.get('player_stats', {})}
            - Inventory: {game_state.get('inventory', [])}
            """
            prompt_parts.append(state_context)

        prompt_parts.append(f"Player input: {user_input}")
        prompt_parts.append("Provide an engaging, atmospheric response as the game master:")

        return "\n".join(prompt_parts)

    def update_game_context(self, new_context: str):
        """Update the base game context used for AI responses"""
        self.game_context = new_context
        logger.info("Updated game context")
