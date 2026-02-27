import logging
import os
import time
from dataclasses import dataclass
import google.generativeai as genai
from google.generativeai.types import generation_types
from app.db.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# Pricing per million tokens (USD) — keep in sync with actual Gemini API model IDs
PRICING = {
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60},
    "gemini-2.5-pro":   {"input": 1.25, "output": 10.00},
}

MAX_RETRIES = 3


@dataclass
class GeminiResponse:
    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    model: str


class GeminiClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        genai.configure(api_key=self.api_key)

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        model_pricing = PRICING.get(model, PRICING["gemini-2.0-flash"])
        cost = (input_tokens * model_pricing["input"] / 1_000_000) + \
               (output_tokens * model_pricing["output"] / 1_000_000)
        return cost

    def _invoke(self, model_name: str, contents, system_instruction=None, temperature: float = 0.1, response_format=None) -> GeminiResponse:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json" if response_format == "json" else None
            )
        )

        start_time = time.time()

        tries = 0
        while tries < MAX_RETRIES:
            try:
                response = model.generate_content(contents)
                break
            except Exception as e:
                if "429" in str(e) or "timeout" in str(e).lower():
                    tries += 1
                    if tries >= MAX_RETRIES:
                        raise
                    time.sleep(2 ** tries)
                else:
                    raise

        latency_ms = int((time.time() - start_time) * 1000)

        # Check safety ratings/empty response
        if not response.parts:
            return GeminiResponse(
                text="",
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                model=model_name
            )

        text = response.text

        input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
        cost_usd = self._calculate_cost(model_name, input_tokens, output_tokens)

        return GeminiResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            model=model_name
        )

    def generate(self, model: str, prompt: str, system_instruction=None, temperature: float = 0.1, response_format=None) -> GeminiResponse:
        return self._invoke(
            model_name=model,
            contents=[prompt],
            system_instruction=system_instruction,
            temperature=temperature,
            response_format=response_format
        )

    def generate_with_image(self, model: str, prompt: str, image_bytes: bytes, mime_type: str, system_instruction=None) -> GeminiResponse:
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        return self._invoke(
            model_name=model,
            contents=[image_part, prompt],
            system_instruction=system_instruction,
            temperature=0.0,
            response_format="json"
        )

    def generate_with_file(self, model: str, prompt: str, file_bytes: bytes, mime_type: str, system_instruction=None) -> GeminiResponse:
        return self.generate_with_image(model, prompt, file_bytes, mime_type, system_instruction)


def log_llm_usage(firm_id: str, project_id: str, model: str, task_type: str, gemini_response: GeminiResponse, success: bool, error_message: str = None) -> None:
    """Log LLM usage to database. Failures are logged as warnings, not propagated."""
    try:
        db = get_supabase()
        db.table("llm_usage_log").insert({
            "firm_id": firm_id,
            "cma_project_id": project_id,
            "model": model,
            "task_type": task_type,
            "input_tokens": gemini_response.input_tokens if gemini_response else 0,
            "output_tokens": gemini_response.output_tokens if gemini_response else 0,
            "cost_usd": gemini_response.cost_usd if gemini_response else 0.0,
            "latency_ms": gemini_response.latency_ms if gemini_response else None,
            "success": success,
            "error_message": error_message
        }).execute()
    except Exception as e:
        logger.warning("Failed to log LLM usage: %s", e)
