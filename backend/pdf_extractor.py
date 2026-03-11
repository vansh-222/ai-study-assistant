"""PDF text extraction utilities."""

import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        A single string containing all extracted text.

    Raises:
        ValueError: If the PDF contains no extractable text.
        FileNotFoundError: If the file does not exist.
    """
    text_parts: list[str] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    extracted = "\n\n".join(text_parts).strip()

    if not extracted:
        raise ValueError("No extractable text found in the PDF.")

    return extracted
