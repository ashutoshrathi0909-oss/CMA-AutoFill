import json
import logging
import os
from typing import Dict, Any
from app.services.gemini_client import GeminiClient, log_llm_usage
from app.services.extraction.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT, JSON_SCHEMA

logger = logging.getLogger(__name__)


def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-len("```")]
    return text.strip()


def extract_with_vision(file_bytes: bytes, filename: str, mime_type: str, firm_id: str, project_id: str, document_type: str = "auto-detect") -> Dict[str, Any]:
    client = GeminiClient()

    model_name = os.getenv("LLM_EXTRACTION_MODEL", "gemini-2.0-flash")

    user_prompt = EXTRACTION_USER_PROMPT.replace("{document_type}", document_type).replace("{json_schema}", JSON_SCHEMA)

    response = client.generate_with_image(
        model=model_name,
        prompt=user_prompt,
        image_bytes=file_bytes,
        mime_type=mime_type,
        system_instruction=EXTRACTION_SYSTEM_PROMPT,
    )

    # Log usage (non-blocking — failures are just warnings)
    log_llm_usage(
        firm_id=firm_id,
        project_id=project_id,
        model=model_name,
        task_type="extraction",
        gemini_response=response,
        success=bool(response.text),
    )

    if not response.text:
        raise ValueError("Failed to extract data: Gemini returned empty response.")

    try:
        json_str = clean_json_text(response.text)
        data = json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}\nRaw Response: {response.text}")

    # Validate required keys exist
    if not isinstance(data, dict):
        raise ValueError(f"Gemini returned non-object JSON: {type(data)}")

    if "line_items" not in data or not isinstance(data.get("line_items"), list):
        raise ValueError(f"Gemini response missing 'line_items' array. Keys found: {list(data.keys())}")

    # Safely set metadata
    data.setdefault("metadata", {})["source_file"] = filename
    data.setdefault("document_type", "other")

    return data
