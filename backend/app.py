"""AI Study Assistant — Flask backend."""

import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from .ai_generator import (
    generate_flashcards,
    generate_mock_test,
    generate_questions,
    generate_study_plan,
)
from .pdf_extractor import extract_text_from_pdf

load_dotenv()

ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    CORS(app)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _allowed_file(filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def _extract_text_from_request() -> tuple[str, dict | None]:
        """Extract text either from an uploaded PDF or from a JSON body.

        Returns:
            A tuple of (text, error_response). If extraction succeeds,
            error_response is None. If it fails, text is empty and
            error_response is a Flask JSON response dict.
        """
        if request.content_type and "multipart/form-data" in request.content_type:
            if "file" not in request.files:
                return "", {"error": "No file provided."}
            file = request.files["file"]
            if file.filename == "":
                return "", {"error": "No file selected."}
            if not _allowed_file(file.filename):
                return "", {"error": "Only PDF files are supported."}

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            try:
                text = extract_text_from_pdf(tmp_path)
            except ValueError as exc:
                return "", {"error": str(exc)}
            finally:
                os.unlink(tmp_path)

            return text, None

        # JSON body with pre-extracted text
        body = request.get_json(silent=True) or {}
        text = body.get("text", "").strip()
        if not text:
            return "", {"error": "Provide either a PDF file or a 'text' field in JSON."}
        return text, None

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.get("/health")
    def health():
        """Health-check endpoint."""
        return jsonify({"status": "ok"})

    @app.post("/extract")
    def extract():
        """Extract text from an uploaded PDF.

        Form data:
            file: PDF file.

        Returns JSON:
            { "text": "<extracted text>" }
        """
        if "file" not in request.files:
            return jsonify({"error": "No file provided."}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected."}), 400
        if not _allowed_file(file.filename):
            return jsonify({"error": "Only PDF files are supported."}), 400

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            text = extract_text_from_pdf(tmp_path)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 422
        finally:
            os.unlink(tmp_path)

        return jsonify({"text": text})

    @app.post("/generate/questions")
    def questions():
        """Generate study questions.

        Accepts multipart PDF upload or JSON body with ``text`` field.

        Optional query param:
            num_questions (int, default 10)

        Returns JSON:
            { "questions": [ { "question": "...", "answer": "..." }, ... ] }
        """
        text, err = _extract_text_from_request()
        if err:
            return jsonify(err), 400

        try:
            num = int(request.args.get("num_questions", 10))
        except ValueError:
            num = 10

        try:
            result = generate_questions(text, num_questions=num)
        except Exception as exc:
            return jsonify({"error": f"AI generation failed: {exc}"}), 500

        return jsonify({"questions": result})

    @app.post("/generate/flashcards")
    def flashcards():
        """Generate flashcards.

        Accepts multipart PDF upload or JSON body with ``text`` field.

        Optional query param:
            num_cards (int, default 10)

        Returns JSON:
            { "flashcards": [ { "front": "...", "back": "..." }, ... ] }
        """
        text, err = _extract_text_from_request()
        if err:
            return jsonify(err), 400

        try:
            num = int(request.args.get("num_cards", 10))
        except ValueError:
            num = 10

        try:
            result = generate_flashcards(text, num_cards=num)
        except Exception as exc:
            return jsonify({"error": f"AI generation failed: {exc}"}), 500

        return jsonify({"flashcards": result})

    @app.post("/generate/study-plan")
    def study_plan():
        """Generate a study plan.

        Accepts multipart PDF upload or JSON body with ``text`` field.

        Optional query param:
            days (int, default 7)

        Returns JSON:
            { "plan": [ { "day": 1, "tasks": ["..."] }, ... ] }
        """
        text, err = _extract_text_from_request()
        if err:
            return jsonify(err), 400

        try:
            days = int(request.args.get("days", 7))
        except ValueError:
            days = 7

        try:
            result = generate_study_plan(text, days=days)
        except Exception as exc:
            return jsonify({"error": f"AI generation failed: {exc}"}), 500

        return jsonify(result)

    @app.post("/generate/mock-test")
    def mock_test():
        """Generate a multiple-choice mock test.

        Accepts multipart PDF upload or JSON body with ``text`` field.

        Optional query param:
            num_questions (int, default 10)

        Returns JSON:
            {
              "questions": [
                {
                  "question": "...",
                  "options": ["A", "B", "C", "D"],
                  "correct_index": 0,
                  "explanation": "..."
                },
                ...
              ]
            }
        """
        text, err = _extract_text_from_request()
        if err:
            return jsonify(err), 400

        try:
            num = int(request.args.get("num_questions", 10))
        except ValueError:
            num = 10

        try:
            result = generate_mock_test(text, num_questions=num)
        except Exception as exc:
            return jsonify({"error": f"AI generation failed: {exc}"}), 500

        return jsonify(result)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
