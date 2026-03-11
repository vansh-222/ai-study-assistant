"""Tests for the Flask application endpoints."""

import io
import json

import pytest

from backend.app import create_app

SAMPLE_TEXT = "Plants use photosynthesis to convert sunlight into energy."

QUESTIONS_JSON = json.dumps(
    [{"question": "What is photosynthesis?", "answer": "Energy conversion process."}]
)
FLASHCARDS_JSON = json.dumps(
    [{"front": "Photosynthesis", "back": "Converts sunlight to energy."}]
)
STUDY_PLAN_JSON = json.dumps(
    {"plan": [{"day": 1, "tasks": ["Read about photosynthesis"]}]}
)
MOCK_TEST_JSON = json.dumps(
    {
        "questions": [
            {
                "question": "What does photosynthesis produce?",
                "options": ["Glucose", "Water", "CO2", "Salt"],
                "correct_index": 0,
                "explanation": "Glucose is the primary product.",
            }
        ]
    }
)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestExtract:
    def test_no_file_returns_400(self, client):
        resp = client.post("/extract")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_non_pdf_returns_400(self, client):
        data = {"file": (io.BytesIO(b"hello"), "hello.txt")}
        resp = client.post("/extract", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_valid_pdf_returns_text(self, client, mocker):
        mocker.patch("backend.app.extract_text_from_pdf", return_value=SAMPLE_TEXT)
        data = {"file": (io.BytesIO(b"%PDF-1.4"), "sample.pdf")}
        resp = client.post("/extract", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        assert resp.get_json()["text"] == SAMPLE_TEXT

    def test_pdf_with_no_text_returns_422(self, client, mocker):
        mocker.patch(
            "backend.app.extract_text_from_pdf",
            side_effect=ValueError("No extractable text found in the PDF."),
        )
        data = {"file": (io.BytesIO(b"%PDF-1.4"), "empty.pdf")}
        resp = client.post("/extract", data=data, content_type="multipart/form-data")
        assert resp.status_code == 422
        assert "error" in resp.get_json()


class TestGenerateQuestions:
    def test_json_text_body(self, client, mocker):
        mocker.patch("backend.app.generate_questions", return_value=json.loads(QUESTIONS_JSON))
        resp = client.post(
            "/generate/questions",
            json={"text": SAMPLE_TEXT},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "questions" in data
        assert len(data["questions"]) == 1

    def test_missing_text_returns_400(self, client):
        resp = client.post("/generate/questions", json={})
        assert resp.status_code == 400

    def test_num_questions_param(self, client, mocker):
        mock_fn = mocker.patch(
            "backend.app.generate_questions", return_value=json.loads(QUESTIONS_JSON)
        )
        client.post("/generate/questions?num_questions=5", json={"text": SAMPLE_TEXT})
        mock_fn.assert_called_once_with(SAMPLE_TEXT, num_questions=5)

    def test_pdf_upload(self, client, mocker):
        mocker.patch("backend.app.extract_text_from_pdf", return_value=SAMPLE_TEXT)
        mocker.patch("backend.app.generate_questions", return_value=json.loads(QUESTIONS_JSON))
        data = {"file": (io.BytesIO(b"%PDF-1.4"), "test.pdf")}
        resp = client.post(
            "/generate/questions",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        assert "questions" in resp.get_json()

    def test_ai_failure_returns_500(self, client, mocker):
        mocker.patch(
            "backend.app.generate_questions", side_effect=RuntimeError("OpenAI down")
        )
        resp = client.post("/generate/questions", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 500
        assert "error" in resp.get_json()


class TestGenerateFlashcards:
    def test_json_text_body(self, client, mocker):
        mocker.patch("backend.app.generate_flashcards", return_value=json.loads(FLASHCARDS_JSON))
        resp = client.post("/generate/flashcards", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        assert "flashcards" in resp.get_json()

    def test_missing_text_returns_400(self, client):
        resp = client.post("/generate/flashcards", json={})
        assert resp.status_code == 400

    def test_num_cards_param(self, client, mocker):
        mock_fn = mocker.patch(
            "backend.app.generate_flashcards", return_value=json.loads(FLASHCARDS_JSON)
        )
        client.post("/generate/flashcards?num_cards=8", json={"text": SAMPLE_TEXT})
        mock_fn.assert_called_once_with(SAMPLE_TEXT, num_cards=8)


class TestGenerateStudyPlan:
    def test_json_text_body(self, client, mocker):
        mocker.patch("backend.app.generate_study_plan", return_value=json.loads(STUDY_PLAN_JSON))
        resp = client.post("/generate/study-plan", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        assert "plan" in resp.get_json()

    def test_missing_text_returns_400(self, client):
        resp = client.post("/generate/study-plan", json={})
        assert resp.status_code == 400

    def test_days_param(self, client, mocker):
        mock_fn = mocker.patch(
            "backend.app.generate_study_plan", return_value=json.loads(STUDY_PLAN_JSON)
        )
        client.post("/generate/study-plan?days=14", json={"text": SAMPLE_TEXT})
        mock_fn.assert_called_once_with(SAMPLE_TEXT, days=14)


class TestGenerateMockTest:
    def test_json_text_body(self, client, mocker):
        mocker.patch("backend.app.generate_mock_test", return_value=json.loads(MOCK_TEST_JSON))
        resp = client.post("/generate/mock-test", json={"text": SAMPLE_TEXT})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "questions" in data
        assert len(data["questions"]) == 1

    def test_missing_text_returns_400(self, client):
        resp = client.post("/generate/mock-test", json={})
        assert resp.status_code == 400

    def test_num_questions_param(self, client, mocker):
        mock_fn = mocker.patch(
            "backend.app.generate_mock_test", return_value=json.loads(MOCK_TEST_JSON)
        )
        client.post("/generate/mock-test?num_questions=15", json={"text": SAMPLE_TEXT})
        mock_fn.assert_called_once_with(SAMPLE_TEXT, num_questions=15)
