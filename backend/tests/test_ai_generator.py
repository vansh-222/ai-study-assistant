"""Tests for the AI generator module."""

import json

import pytest


SAMPLE_TEXT = (
    "Photosynthesis is the process by which plants convert sunlight, water, and "
    "carbon dioxide into glucose and oxygen. Chlorophyll is the pigment responsible "
    "for absorbing light energy."
)

QUESTIONS_RESPONSE = json.dumps(
    [
        {"question": "What is photosynthesis?", "answer": "The process plants use to make food."},
        {"question": "What does chlorophyll do?", "answer": "Absorbs light energy."},
    ]
)

FLASHCARDS_RESPONSE = json.dumps(
    [
        {"front": "Photosynthesis", "back": "Process of converting sunlight to glucose."},
        {"front": "Chlorophyll", "back": "Pigment that absorbs light."},
    ]
)

STUDY_PLAN_RESPONSE = json.dumps(
    {
        "plan": [
            {"day": 1, "tasks": ["Read chapter on photosynthesis", "Take notes"]},
            {"day": 2, "tasks": ["Review chlorophyll", "Practice questions"]},
        ]
    }
)

MOCK_TEST_RESPONSE = json.dumps(
    {
        "questions": [
            {
                "question": "What is photosynthesis?",
                "options": ["A process", "A chemical", "A plant", "A gas"],
                "correct_index": 0,
                "explanation": "Photosynthesis is a biological process.",
            }
        ]
    }
)


class TestGenerateQuestions:
    def test_returns_list_of_questions(self, mocker):
        from backend.ai_generator import generate_questions

        mocker.patch("backend.ai_generator._chat", return_value=QUESTIONS_RESPONSE)
        result = generate_questions(SAMPLE_TEXT, num_questions=2)

        assert isinstance(result, list)
        assert len(result) == 2
        assert "question" in result[0]
        assert "answer" in result[0]

    def test_passes_num_questions_to_prompt(self, mocker):
        from backend.ai_generator import generate_questions

        mock_chat = mocker.patch("backend.ai_generator._chat", return_value=QUESTIONS_RESPONSE)
        generate_questions(SAMPLE_TEXT, num_questions=5)

        _, user_prompt = mock_chat.call_args[0]
        assert "5" in user_prompt

    def test_raises_on_invalid_json(self, mocker):
        from backend.ai_generator import generate_questions

        mocker.patch("backend.ai_generator._chat", return_value="not json")
        with pytest.raises(json.JSONDecodeError):
            generate_questions(SAMPLE_TEXT)

    def test_strips_code_fences(self, mocker):
        from backend.ai_generator import generate_questions

        wrapped = f"```json\n{QUESTIONS_RESPONSE}\n```"
        mocker.patch("backend.ai_generator._chat", return_value=wrapped)
        result = generate_questions(SAMPLE_TEXT, num_questions=2)

        assert isinstance(result, list)
        assert len(result) == 2


class TestGenerateFlashcards:
    def test_returns_list_of_flashcards(self, mocker):
        from backend.ai_generator import generate_flashcards

        mocker.patch("backend.ai_generator._chat", return_value=FLASHCARDS_RESPONSE)
        result = generate_flashcards(SAMPLE_TEXT, num_cards=2)

        assert isinstance(result, list)
        assert len(result) == 2
        assert "front" in result[0]
        assert "back" in result[0]

    def test_passes_num_cards_to_prompt(self, mocker):
        from backend.ai_generator import generate_flashcards

        mock_chat = mocker.patch("backend.ai_generator._chat", return_value=FLASHCARDS_RESPONSE)
        generate_flashcards(SAMPLE_TEXT, num_cards=8)

        _, user_prompt = mock_chat.call_args[0]
        assert "8" in user_prompt


class TestGenerateStudyPlan:
    def test_returns_dict_with_plan(self, mocker):
        from backend.ai_generator import generate_study_plan

        mocker.patch("backend.ai_generator._chat", return_value=STUDY_PLAN_RESPONSE)
        result = generate_study_plan(SAMPLE_TEXT, days=2)

        assert isinstance(result, dict)
        assert "plan" in result
        assert len(result["plan"]) == 2
        assert "day" in result["plan"][0]
        assert "tasks" in result["plan"][0]

    def test_passes_days_to_prompt(self, mocker):
        from backend.ai_generator import generate_study_plan

        mock_chat = mocker.patch("backend.ai_generator._chat", return_value=STUDY_PLAN_RESPONSE)
        generate_study_plan(SAMPLE_TEXT, days=14)

        _, user_prompt = mock_chat.call_args[0]
        assert "14" in user_prompt


class TestGenerateMockTest:
    def test_returns_dict_with_questions(self, mocker):
        from backend.ai_generator import generate_mock_test

        mocker.patch("backend.ai_generator._chat", return_value=MOCK_TEST_RESPONSE)
        result = generate_mock_test(SAMPLE_TEXT, num_questions=1)

        assert isinstance(result, dict)
        assert "questions" in result
        q = result["questions"][0]
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) == 4
        assert "correct_index" in q
        assert "explanation" in q

    def test_passes_num_questions_to_prompt(self, mocker):
        from backend.ai_generator import generate_mock_test

        mock_chat = mocker.patch("backend.ai_generator._chat", return_value=MOCK_TEST_RESPONSE)
        generate_mock_test(SAMPLE_TEXT, num_questions=20)

        _, user_prompt = mock_chat.call_args[0]
        assert "20" in user_prompt
