import json
import re
from typing import Any, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import log_fallback_used

T = TypeVar("T", bound=BaseModel)


def _build_doubao_llm(temperature: float = 0.2) -> ChatOpenAI:
    """Build a ChatOpenAI instance pointing to Volcano Engine (Doubao)."""
    if not settings.doubao_api_key:
        raise RuntimeError("DOUBAO_API_KEY not configured")
    if not settings.doubao_model:
        raise RuntimeError("DOUBAO_MODEL (endpoint ID) not configured")

    return ChatOpenAI(
        base_url=settings.doubao_base_url,
        api_key=settings.doubao_api_key,
        model=settings.doubao_model,
        temperature=temperature,
        max_retries=1,
        timeout=180,
        max_completion_tokens=8192,
    )


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
        return "\n".join(parts)
    return str(content)


def _parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("LLM response must be a JSON object")
    return parsed


class LLMAdapter:
    """Unified LLM adapter supporting Doubao Seed via Volcano Engine OpenAI-compatible API."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self._llm: ChatOpenAI | None = None

    def _get_llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = _build_doubao_llm()
        return self._llm

    def generate_structured(
        self,
        prompt_name: str,
        inputs: dict[str, Any],
        output_schema: type[T],
        system_prompt: str | None = None,
        metadata: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> T:
        """Generate structured output from LLM using Pydantic schema.

        Args:
            prompt_name: Identifier for logging
            inputs: Data to embed in the prompt (rendered as JSON)
            output_schema: Pydantic model class defining expected output shape
            system_prompt: System prompt override (defaults to JSON-mode assistant)
            metadata: Task/run metadata for logging
            temperature: Sampling temperature

        Returns:
            Parsed Pydantic model instance
        """
        task_id = (metadata or {}).get("task_id", "unknown")
        run_id = (metadata or {}).get("run_id", "unknown")

        if self.provider != "doubao":
            raise RuntimeError(
                f"LLM provider is '{self.provider}', but only 'doubao' is supported for real execution. "
                "Set LLM_PROVIDER=doubao and configure DOUBAO_API_KEY + DOUBAO_MODEL."
            )

        llm = _build_doubao_llm(temperature=temperature)

        sys_prompt = system_prompt or (
            "You are a precise analytical AI assistant. "
            "You always respond with valid structured data matching the requested schema exactly. "
            "Do not include explanations outside the structured output. "
            "If data is insufficient, still produce the best possible output within the schema."
        )

        user_prompt = f"""# Task: {prompt_name}

Please analyze the following input data and produce a structured response.

## Input Data

```json
{json.dumps(inputs, ensure_ascii=False, indent=2, default=str)}
```

## Instructions

Produce a single valid JSON object strictly according to this JSON Schema:

```json
{json.dumps(output_schema.model_json_schema(), ensure_ascii=False, indent=2, default=str)}
```

Do not wrap the JSON in Markdown fences.
"""

        messages = [
            SystemMessage(content=sys_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            raw = llm.invoke(messages)
            raw_content = _message_content_to_text(raw.content)
            try:
                parsed = _parse_json_object(raw_content)
            except Exception as parse_error:
                log_fallback_used(
                    task_id=task_id,
                    run_id=run_id,
                    fallback_type="json_repair_retry",
                    reason=f"Initial JSON parse failed for '{prompt_name}': {parse_error}",
                )
                repair_messages = [
                    SystemMessage(
                        content=(
                            "You repair invalid JSON. Return only one valid JSON object. "
                            "Do not add commentary or Markdown fences."
                        )
                    ),
                    HumanMessage(
                        content=f"""Repair the following model output so it becomes valid JSON matching this schema.

## JSON Schema

```json
{json.dumps(output_schema.model_json_schema(), ensure_ascii=False, indent=2, default=str)}
```

## Invalid Output

{raw_content}
"""
                    ),
                ]
                repaired = llm.invoke(repair_messages)
                parsed = _parse_json_object(_message_content_to_text(repaired.content))
            return output_schema.model_validate(parsed)
        except Exception as e:
            # Log and re-raise — no silent fallback to mock
            log_fallback_used(
                task_id=task_id,
                run_id=run_id,
                fallback_type="structured_output_failed",
                reason=f"Doubao structured output failed: {e}",
            )
            raise RuntimeError(f"LLM call failed for '{prompt_name}': {e}") from e


llm_adapter = LLMAdapter()
