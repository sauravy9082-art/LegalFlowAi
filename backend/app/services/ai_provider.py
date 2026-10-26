from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    """
    Abstract AI Provider Interface for LegalFlow AI.
    Rule 4 & Rule 3: Ollama is the ONLY allowed AI/LLM engine.
    Cloud LLMs (OpenAI, Gemini, Anthropic) are explicitly forbidden.
    """

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def generate_structured_json(self, prompt: str, schema_class: Any, system_prompt: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        pass
