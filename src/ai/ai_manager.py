from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging
import anthropic

try:
    import openai
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    openai = None

try:
    import google.generativeai as genai
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    genai = None

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


class OpenAIBackend(AIModelBackend):
    """OpenAI API backend"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if openai and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("Successfully initialized OpenAI backend")
        else:
            self.client = None
            logger.warning("OpenAI package not available or API key missing")

    def generate_response(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OpenAI backend not configured")

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {e}")
            raise

    def is_available(self) -> bool:
        return self.client is not None


class GeminiBackend(AIModelBackend):
    """Google Gemini API backend"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel("gemini-pro")
                logger.info("Successfully initialized Gemini backend")
            except Exception as e:
                self.model = None
                logger.error(f"Failed to initialize Gemini model: {e}")
        else:
            self.model = None
            logger.warning(
                "google-generativeai package not available or API key missing"
            )

    def generate_response(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Gemini backend not configured")

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            raise

    def is_available(self) -> bool:
        return self.model is not None


class OpenRouterBackend(AIModelBackend):
    """OpenRouter API backend (OpenAI-compatible)"""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        if openai and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info("Successfully initialized OpenRouter backend")
        else:
            self.client = None
            logger.warning("OpenRouter API key missing or openai package not available")

    def generate_response(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("OpenRouter backend not configured")

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "openrouter/mistral-7b"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting OpenRouter response: {e}")
            raise

    def is_available(self) -> bool:
        return self.client is not None


class AIManager:
    def __init__(self):
        load_dotenv()

        # Initialize backends
        self.backends = {
            "claude": ClaudeBackend(),
            "llama": LlamaBackend(),
            "openai": OpenAIBackend(),
            "gemini": GeminiBackend(),
            "openrouter": OpenRouterBackend(),
        }

        env_backend = os.getenv("DEFAULT_AI_BACKEND", "claude")
        if env_backend in self.backends and self.backends[env_backend].is_available():
            self._current_backend = env_backend
        else:
            backend = self.backends.get(env_backend)
            invalid_default = env_backend not in self.backends or not (backend.is_available() if backend else False)
            if invalid_default:
                logger.warning(
                    f"Invalid DEFAULT_AI_BACKEND '{env_backend}' - attempting to find an available backend"
                )
                for name, backend in self.backends.items():
                    if backend.is_available():
                        self._current_backend = name
                        logger.info(f"Falling back to available backend: '{name}'")
                        break
                else:
                    raise RuntimeError("No available AI backends found.")
            else:
                self._current_backend = env_backend

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
