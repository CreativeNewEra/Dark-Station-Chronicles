from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
import anthropic

try:
    from llama_cpp import Llama
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    Llama = None
import os
from dotenv import load_dotenv
from datetime import datetime

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
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
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
        if Llama is None:
            self.model = None
            logger.warning("llama_cpp package not available; Llama backend disabled")
        elif model_path and os.path.exists(model_path):
            try:
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=2048,
                    n_threads=4,
                    n_gpu_layers=32,  # This enables GPU acceleration
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
                prompt, max_tokens=512, temperature=0.7, stop=["Human:", "Assistant:"]
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Error getting Llama response: {e}")
            raise

    def is_available(self) -> bool:
        return self.model is not None


class AIManager:
    def __init__(self):
        load_dotenv()

        # Initialize backends
        self.backends = {"claude": ClaudeBackend(), "llama": LlamaBackend()}

        self._current_backend = os.getenv("DEFAULT_AI_BACKEND", "claude")

        # Conversation memory
        self.conversation_history = []
        self.memory_limit = 10  # Keep last 10 exchanges

        # Enhanced game context with character classes
        self.game_context = {
            "base": """You are the AI game master for Dark Station Chronicles.
                    The game is set in an abandoned space station where mysterious events occur.""",
            "cybernetic": """Use technical, precise language. Reference cybernetic enhancements
                         and technological solutions. Interface with station systems.""",
            "psionic": """Use mystical, ethereal language. Reference psychic phenomena
                      and emotional undercurrents. Sense station mysteries.""",
            "hunter": """Use tactical, survival-focused language. Reference tracking,
                     stealth, and resource management. Analyze station threats.""",
        }

    @property
    def current_backend(self) -> str:
        """Get the name of the current backend"""
        return self._current_backend

    def switch_backend(self, name: str) -> bool:
        """Attempt to switch the active backend.

        Parameters
        ----------
        name: str
            Name of the backend to activate.

        Returns
        -------
        bool
            ``True`` if the backend exists, is available and was activated,
            ``False`` otherwise.
        """
        if name == self._current_backend:
            current_backend = self.backends.get(self._current_backend)
            if current_backend and current_backend.is_available():
                return True
            logger.warning(
                f"Current backend '{self._current_backend}' is not available"
            )
            return False

        backend = self.backends.get(name)
        if backend and backend.is_available():
            self._current_backend = name
            logger.info(f"Switched AI backend to {name}")
            return True

        if not backend:
            logger.warning(
                f"Requested backend '{name}' does not exist in the available backends"
            )
        elif not backend.is_available():
            logger.warning(f"Requested backend '{name}' exists but is not available")
        return False

    def _construct_prompt(
        self, user_input: str, game_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct the full prompt including context and conversation history"""
        prompt_parts = []

        # Add base context
        prompt_parts.append(self.game_context["base"])

        # Add character-specific context if available
        if game_state and "character_class" in game_state:
            char_class = game_state["character_class"]
            if char_class in self.game_context:
                prompt_parts.append(self.game_context[char_class])

        # Add relevant conversation history
        if self.conversation_history:
            history = "\nRecent interactions:\n"
            for exchange in self.conversation_history[-self.memory_limit :]:
                history += f"Player: {exchange['input']}\n"
                history += f"Response: {exchange['response']}\n"
            prompt_parts.append(history)

        # Add current game state
        if game_state:
            state_context = f"""
            Current game state:
            - Location: {game_state.get('current_room', 'unknown')}
            - Player stats: {game_state.get('player_stats', {})}
            - Inventory: {game_state.get('inventory', [])}
            """
            prompt_parts.append(state_context)

        prompt_parts.append(f"Player input: {user_input}")
        return "\n".join(prompt_parts)

    def get_ai_response(
        self, prompt: str, game_state: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            backend = self.backends[self._current_backend]
            if not backend.is_available():
                # Try to fall back to another available backend
                for name, fallback in self.backends.items():
                    if name != self._current_backend and fallback.is_available():
                        logger.info(f"Falling back to {name} backend")
                        backend = fallback
                        break
                else:
                    raise RuntimeError("No AI backends available")

            full_prompt = self._construct_prompt(prompt, game_state)
            response = backend.generate_response(full_prompt)

            # Store the exchange in conversation history
            self.conversation_history.append(
                {
                    "input": prompt,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I encountered an error processing your request."
