
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIModel:
    """Common interface for SkillForge AI models."""

    def get_hint(
        self,
        challenge: str,
        code: str,
        error_message: str = "",
    ) -> str:
        raise NotImplementedError

    def classify_error(self, error_message: str) -> str:
        raise NotImplementedError


class OpenAIModel(AIModel):
    """Cloud-based model for detailed coding assistance."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to your .env file."
            )

        self.client = OpenAI(api_key=api_key)
        self.model_name = os.getenv(
            "OPENAI_MODEL", "gpt-4.1-mini"
        )

    def _ask(self, instructions: str, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            instructions=instructions,
            input=prompt,
        )
        return response.output_text.strip()

    def get_hint(
        self,
        challenge: str,
        code: str,
        error_message: str = "",
    ) -> str:
        return self._ask(
            instructions=(
                "You are SkillForge AI, a patient programming mentor. "
                "Help fresh graduates learn practical coding. "
                "Give a useful hint first, explain the reasoning, "
                "and do not immediately reveal the full solution."
            ),
            prompt=(
                f"Challenge:\n{challenge}\n\n"
                f"Learner code:\n{code}\n\n"
                f"Error message:\n{error_message}\n\n"
                "Identify the likely issue and give one actionable hint."
            ),
        )

    def classify_error(self, error_message: str) -> str:
        return self._ask(
            instructions=(
                "Classify programming errors concisely. "
                "Return a category and one-sentence explanation."
            ),
            prompt=(
                f"Classify this error: {error_message}\n\n"
                "Choose a category such as syntax, type, logic, "
                "runtime, dependency, or unknown."
            ),
        )


class GemmaModel(AIModel):
    """
    Local Gemma model using Ollama's local HTTP API.

    Install Ollama and download a compatible Gemma model first.
    Set GEMMA_MODEL to the exact model tag available locally.
    """

    def __init__(self):
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "Install requests with: pip install requests"
            ) from exc

        self.requests = requests
        self.base_url = os.getenv(
            "OLLAMA_URL", "http://localhost:11434"
        ).rstrip("/")
        self.model_name = os.getenv(
            "GEMMA_MODEL", "gemma2:2b"
        )

    def _ask(self, prompt: str) -> str:
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json().get("response", "").strip()

            if not result:
                raise RuntimeError("The local model returned no text.")

            return result

        except self.requests.RequestException as exc:
            raise RuntimeError(
                "Could not reach Ollama. Check that it is running "
                "and that the configured model is installed."
            ) from exc

    def get_hint(
        self,
        challenge: str,
        code: str,
        error_message: str = "",
    ) -> str:
        return self._ask(
            "You are a beginner-friendly coding mentor. "
            "Give one short hint, not the complete solution.\n\n"
            f"Challenge:\n{challenge}\n\n"
            f"Code:\n{code}\n\n"
            f"Error:\n{error_message}\n\n"
            "Explain what the learner should investigate next."
        )

    def classify_error(self, error_message: str) -> str:
        return self._ask(
            "Classify this programming error into one category: "
            "syntax, type, logic, runtime, dependency, or unknown. "
            "Give a short explanation.\n\n"
            f"Error:\n{error_message}"
        )


def get_model(provider: Optional[str] = None) -> AIModel:
    """
    Choose a provider using an argument or the AI_PROVIDER setting.

    Supported values: openai, gemma.
    """
    provider = (
        provider or os.getenv("AI_PROVIDER", "openai")
    ).strip().lower()

    if provider == "openai":
        return OpenAIModel()

    if provider == "gemma":
        return GemmaModel()

    raise ValueError(
        f"Unknown AI provider: {provider}. "
        "Choose 'openai' or 'gemma'."
    )
