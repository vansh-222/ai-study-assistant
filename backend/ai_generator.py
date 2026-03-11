"""AI generation utilities using OpenAI."""

import json
import os

from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Return a shared OpenAI client, creating it on first use."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def _chat(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """Send a chat completion request and return the response text."""
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def generate_questions(text: str, num_questions: int = 10) -> list[dict]:
    """Generate study questions from the given text.

    Args:
        text: The source text to base questions on.
        num_questions: How many questions to generate.

    Returns:
        A list of dicts with keys ``question`` and ``answer``.
    """
    system = (
        "You are an expert educator. Generate clear, concise study questions "
        "from the provided text. Return ONLY valid JSON — a list of objects, "
        'each with "question" and "answer" keys.'
    )
    user = (
        f"Generate {num_questions} study questions from the following text:\n\n{text}"
    )
    raw = _chat(system, user)
    return _parse_json_list(raw)


def generate_flashcards(text: str, num_cards: int = 10) -> list[dict]:
    """Generate flashcards from the given text.

    Args:
        text: The source text.
        num_cards: Number of flashcard pairs to generate.

    Returns:
        A list of dicts with keys ``front`` and ``back``.
    """
    system = (
        "You are an expert educator. Create concise flashcards from the provided "
        "text. Return ONLY valid JSON — a list of objects, "
        'each with "front" (term/concept) and "back" (definition/explanation) keys.'
    )
    user = f"Generate {num_cards} flashcards from the following text:\n\n{text}"
    raw = _chat(system, user)
    return _parse_json_list(raw)


def generate_study_plan(text: str, days: int = 7) -> dict:
    """Generate a day-by-day study plan from the given text.

    Args:
        text: The source text.
        days: Number of days to spread the plan over.

    Returns:
        A dict with key ``plan`` containing a list of daily study tasks,
        where each item has ``day`` and ``tasks`` keys.
    """
    system = (
        "You are an expert learning coach. Create a structured, realistic study plan "
        "based on the provided content. Return ONLY valid JSON with a single key "
        '"plan" whose value is a list of objects each having "day" (integer) and '
        '"tasks" (list of strings) keys.'
    )
    user = (
        f"Create a {days}-day study plan based on the following content:\n\n{text}"
    )
    raw = _chat(system, user)
    return _parse_json_object(raw)


def generate_mock_test(text: str, num_questions: int = 10) -> dict:
    """Generate a multiple-choice mock test from the given text.

    Args:
        text: The source text.
        num_questions: Number of MCQ questions to generate.

    Returns:
        A dict with key ``questions`` containing a list of MCQ objects.
        Each object has ``question``, ``options`` (list of 4 strings),
        ``correct_index`` (0-based int), and ``explanation`` keys.
    """
    system = (
        "You are an expert exam setter. Create a multiple-choice mock test from the "
        "provided text. Return ONLY valid JSON with a single key \"questions\" whose "
        "value is a list of objects, each having: "
        '"question" (string), '
        '"options" (list of exactly 4 strings), '
        '"correct_index" (0-based integer index of the correct option), '
        '"explanation" (brief explanation of the correct answer).'
    )
    user = (
        f"Generate a mock test with {num_questions} multiple-choice questions "
        f"from the following text:\n\n{text}"
    )
    raw = _chat(system, user)
    return _parse_json_object(raw)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first line (```json or ```) and last line (```)
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner).strip()
    return text


def _parse_json_list(raw: str) -> list:
    cleaned = _strip_code_fences(raw)
    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list, got: {type(data)}")
    return data


def _parse_json_object(raw: str) -> dict:
    cleaned = _strip_code_fences(raw)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got: {type(data)}")
    return data
