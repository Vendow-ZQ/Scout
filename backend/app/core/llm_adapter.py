import json
from typing import Any, TypeVar

from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import log_fallback_used

T = TypeVar("T", bound=BaseModel)


class MockLLMResponse:
    """Mock LLM for stable demo without external API."""

    def generate_structured(
        self,
        prompt_name: str,
        inputs: dict[str, Any],
        output_schema: type[T],
        metadata: dict[str, Any] | None = None,
    ) -> T:
        task_id = (metadata or {}).get("task_id", "unknown")
        run_id = (metadata or {}).get("run_id", "unknown")

        # For demo stability, return a minimally valid instance
        # with default/empty values based on the schema
        return output_schema.model_construct(**{})


class LLMAdapter:
    """Unified LLM adapter supporting Doubao Seed and Mock LLM."""

    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self.mock = MockLLMResponse()

    def generate_structured(
        self,
        prompt_name: str,
        inputs: dict[str, Any],
        output_schema: type[T],
        metadata: dict[str, Any] | None = None,
    ) -> T:
        task_id = (metadata or {}).get("task_id", "unknown")
        run_id = (metadata or {}).get("run_id", "unknown")

        if self.provider == "mock":
            return self.mock.generate_structured(
                prompt_name, inputs, output_schema, metadata
            )

        # TODO: Implement Doubao Seed integration
        # For now, fallback to mock
        log_fallback_used(
            task_id=task_id,
            run_id=run_id,
            fallback_type="mock_llm",
            reason="Doubao adapter not yet implemented, falling back to mock",
        )
        return self.mock.generate_structured(
            prompt_name, inputs, output_schema, metadata
        )


llm_adapter = LLMAdapter()
