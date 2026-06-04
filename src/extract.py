"""
extract.py — Extract text from the Nepali budget PDF using pdfplumber.
Cleans ZWJ, ZWNJ, non-breaking spaces, and other invisible Unicode artifacts.
"""

import re
import pdfplumber


def clean_text(text: str) -> str:
    """Remove ZWJ, ZWNJ, non-breaking spaces, and normalise whitespace."""
    # Remove Zero-Width Joiner and Zero-Width Non-Joiner
    text = text.replace("\u200d", "")   # ZWJ
    text = text.replace("\u200c", "")   # ZWNJ
    # Remove other zero-width characters
    text = text.replace("\u200b", "")   # Zero-Width Space
    text = text.replace("\ufeff", "")   # BOM / Zero-Width No-Break Space
    # Replace non-breaking spaces with normal spaces
    text = text.replace("\u00a0", " ")
    # Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(pdf_path: str) -> list[dict]:
    """
    Extract text from every page of the PDF.

    Returns a list of dicts:
        [{"page_number": int, "text": str}, ...]
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                cleaned = clean_text(text)
                if cleaned:
                    pages.append({
                        "page_number": i + 1,
                        "text": cleaned,
                    })
    return pages


if __name__ == "__main__":
    pages = extract_pages("data/budget_82-83.pdf")
    print(f"✅ Extracted {len(pages)} pages")
    if pages:
        print(f"\n--- Sample (page 1) ---")
        print(pages[0]["text"][:500])
