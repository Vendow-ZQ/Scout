from pathlib import Path

PROMPT_ROOT = Path(__file__).resolve().parent.parent / "prompts" / "agents"


def load_agent_prompt(agent_name: str) -> str:
    """Load an agent system prompt from a Markdown file."""
    normalized = agent_name.strip().lower()
    if not normalized or any(part in normalized for part in ("..", "/", "\\")):
        raise ValueError(f"Invalid agent prompt name: {agent_name}")

    prompt_path = PROMPT_ROOT / f"{normalized}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Agent prompt not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()
