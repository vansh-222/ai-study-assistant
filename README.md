# AI Study Assistant

An AI-powered study assistant that extracts text from PDFs and generates **questions**, **flashcards**, **study plans**, and **mock tests** using OpenAI.

---

## Features

| Feature | Description |
|---|---|
| 📄 PDF Text Extraction | Upload any PDF; the backend extracts all readable text. |
| ❓ Question Generation | AI generates Q&A pairs to test comprehension. |
| 🃏 Flashcards | Term/definition flashcard pairs with a flip animation. |
| 📅 Study Plan | A day-by-day study schedule tailored to the content. |
| 📝 Mock Test | Multiple-choice exam with instant scoring and explanations. |

---

## Quick Start

### 1. Clone & install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
cp .env.example .env
# Edit .env and add your key:
# OPENAI_API_KEY=sk-...
```

### 3. Run the backend

```bash
python -m backend.app
# Server starts at http://localhost:5000
```

### 4. Open the frontend

Open `frontend/index.html` in your browser (or serve it with any static server).

---

## API Reference

All generation endpoints accept either:
- A **multipart form upload** with `file` (PDF), or
- A **JSON body** with a `text` field (pre-extracted text).

| Method | Endpoint | Query params | Response |
|---|---|---|---|
| GET | `/health` | — | `{ "status": "ok" }` |
| POST | `/extract` | — | `{ "text": "..." }` |
| POST | `/generate/questions` | `num_questions` (default 10) | `{ "questions": [...] }` |
| POST | `/generate/flashcards` | `num_cards` (default 10) | `{ "flashcards": [...] }` |
| POST | `/generate/study-plan` | `days` (default 7) | `{ "plan": [...] }` |
| POST | `/generate/mock-test` | `num_questions` (default 10) | `{ "questions": [...] }` |

---

## Running Tests

```bash
pytest
```

---

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── app.py            # Flask application
│   ├── pdf_extractor.py  # PDF text extraction
│   ├── ai_generator.py   # OpenAI generation utilities
│   └── tests/
│       ├── test_app.py
│       ├── test_ai_generator.py
│       └── test_pdf_extractor.py
├── frontend/
│   ├── index.html        # Single-page UI
│   ├── style.css
│   └── app.js
├── .env.example
├── requirements.txt
└── pytest.ini
```