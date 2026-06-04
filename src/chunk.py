"""
chunk.py — Split extracted pages into semantic chunks for embedding.

Strategy:
  1. Detect Devanagari numbered sections (१., २., …) and keyword headings
     (कार्यक्रम, मन्त्रालय, बजेट विनियोजन, etc.).
  2. Split on those headings to create semantically coherent chunks.
  3. Enforce max 500 words / min 50 words per chunk with 50-word overlap.
"""

import re

# ── Heading patterns ──────────────────────────────────────────────────────────

# Devanagari digits for numbered sections like "१.", "१.२", "१.२.३"
_DEVANAGARI_NUMBERED = re.compile(
    r"^[०-९]+(?:\.[०-९]+)*[\.\)]\s+",
    re.MULTILINE,
)

# Keyword-based headings common in Nepali budget documents
_KEYWORD_HEADINGS = [
    "कार्यक्रम",
    "मन्त्रालय",
    "बजेट विनियोजन",
    "विनियोजन",
    "योजना",
    "राजस्व",
    "व्यय",
    "अनुदान",
    "ऋण",
    "कोष",
    "आर्थिक",
    "वित्तीय",
    "सामाजिक",
    "पूँजीगत",
    "चालु",
    "शीर्षक",
    "परिच्छेद",
    "भाग",
    "अध्याय",
    "खण्ड",
]

_KEYWORD_PATTERN = re.compile(
    r"^(" + "|".join(re.escape(k) for k in _KEYWORD_HEADINGS) + r")\b",
    re.MULTILINE,
)

MAX_WORDS = 500
MIN_WORDS = 50
OVERLAP_WORDS = 50


def _word_count(text: str) -> int:
    return len(text.split())


def _detect_section_title(text: str) -> str:
    """Try to extract a section title from the first line of a chunk."""
    first_line = text.strip().split("\n")[0].strip()
    # Truncate if too long
    if len(first_line) > 120:
        first_line = first_line[:120] + "…"
    return first_line


def _detect_ministry(text: str) -> str:
    """Try to detect ministry name from text. Look for 'मन्त्रालय' keyword."""
    for line in text.split("\n"):
        line = line.strip()
        if "मन्त्रालय" in line and len(line) < 150:
            return line
    return ""


def _split_on_headings(text: str) -> list[str]:
    """Split text at Devanagari section headings."""
    # Find all heading positions
    positions = []
    for m in _DEVANAGARI_NUMBERED.finditer(text):
        positions.append(m.start())
    for m in _KEYWORD_PATTERN.finditer(text):
        positions.append(m.start())

    if not positions:
        return [text]

    positions = sorted(set(positions))
    segments = []
    for i, pos in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        segment = text[pos:end].strip()
        if segment:
            segments.append(segment)

    # Include any text before the first heading
    if positions[0] > 0:
        preamble = text[: positions[0]].strip()
        if preamble:
            segments.insert(0, preamble)

    return segments


def _enforce_size_limits(segments: list[str]) -> list[str]:
    """Enforce max/min word limits with overlap."""
    final_chunks = []

    for segment in segments:
        words = segment.split()
        if len(words) <= MAX_WORDS:
            final_chunks.append(segment)
        else:
            # Split into overlapping windows
            start = 0
            while start < len(words):
                end = min(start + MAX_WORDS, len(words))
                chunk_words = words[start:end]
                final_chunks.append(" ".join(chunk_words))
                start += MAX_WORDS - OVERLAP_WORDS

    # Merge tiny chunks with neighbours
    merged = []
    for chunk in final_chunks:
        if merged and _word_count(merged[-1]) < MIN_WORDS:
            merged[-1] = merged[-1] + "\n" + chunk
        elif _word_count(chunk) < MIN_WORDS and merged:
            merged[-1] = merged[-1] + "\n" + chunk
        else:
            merged.append(chunk)

    return merged


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Take extracted pages and produce semantic chunks.

    Input:  [{"page_number": int, "text": str}, ...]
    Output: [{"text": str, "section_title": str,
              "page_number": int, "ministry": str}, ...]
    """
    all_chunks = []

    for page in pages:
        page_num = page["page_number"]
        text = page["text"]

        # Split on headings
        segments = _split_on_headings(text)

        # Enforce size limits
        sized_segments = _enforce_size_limits(segments)

        for seg in sized_segments:
            all_chunks.append({
                "text": seg,
                "section_title": _detect_section_title(seg),
                "page_number": page_num,
                "ministry": _detect_ministry(seg),
            })

    return all_chunks


if __name__ == "__main__":
    from extract import extract_pages

    pages = extract_pages("data/budget_82-83.pdf")
    chunks = chunk_pages(pages)
    print(f"✅ Created {len(chunks)} chunks from {len(pages)} pages")
    if chunks:
        c = chunks[0]
        print(f"\n--- Sample chunk ---")
        print(f"Section : {c['section_title']}")
        print(f"Page    : {c['page_number']}")
        print(f"Ministry: {c['ministry']}")
        print(f"Words   : {_word_count(c['text'])}")
        print(f"Text    : {c['text'][:300]}…")
