"""Tests for pdf_extractor module."""

import io
import os
import tempfile

import pdfplumber
import pytest

# We patch pdfplumber.open to avoid needing real PDF files.


def _make_mock_page(text):
    """Return a mock page object with extract_text returning text."""

    class MockPage:
        def extract_text(self):
            return text

    return MockPage()


class TestExtractTextFromPdf:
    def test_extracts_text_from_pages(self, tmp_path, mocker):
        from backend.pdf_extractor import extract_text_from_pdf

        pages = [_make_mock_page("Page one content."), _make_mock_page("Page two content.")]
        mock_pdf = mocker.MagicMock()
        mock_pdf.__enter__ = mocker.MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf.pages = pages
        mocker.patch("pdfplumber.open", return_value=mock_pdf)

        result = extract_text_from_pdf("dummy.pdf")

        assert "Page one content." in result
        assert "Page two content." in result

    def test_raises_when_no_text(self, mocker):
        from backend.pdf_extractor import extract_text_from_pdf

        pages = [_make_mock_page(None), _make_mock_page("")]
        mock_pdf = mocker.MagicMock()
        mock_pdf.__enter__ = mocker.MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf.pages = pages
        mocker.patch("pdfplumber.open", return_value=mock_pdf)

        with pytest.raises(ValueError, match="No extractable text"):
            extract_text_from_pdf("empty.pdf")

    def test_skips_none_pages(self, mocker):
        from backend.pdf_extractor import extract_text_from_pdf

        pages = [_make_mock_page(None), _make_mock_page("Valid text here.")]
        mock_pdf = mocker.MagicMock()
        mock_pdf.__enter__ = mocker.MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = mocker.MagicMock(return_value=False)
        mock_pdf.pages = pages
        mocker.patch("pdfplumber.open", return_value=mock_pdf)

        result = extract_text_from_pdf("dummy.pdf")
        assert result == "Valid text here."
