"""
prompt.py — Build a grounded RAG prompt with Mr. Wagle persona.

Mr. Wagle is the digital representative of Dr. स्वर्णिम वाग्ले,
Nepal's Finance Minister, who explains budget matters in simple,
human-friendly language.
"""

# Max words per chunk in the prompt to stay within Groq token limits
MAX_CHUNK_WORDS = 200


def _truncate(text: str, max_words: int = MAX_CHUNK_WORDS) -> str:
    """Truncate text to max_words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " …"


SYSTEM_PROMPT = """You are Mr. Wagle — the digital representative of Dr. Swarnim Wagle, Nepal's Finance Minister.

YOUR TASKS:
- Explain budget details in simple, human-friendly language.
- Explain complex economic terms simply.
- Do NOT hallucinate information outside the provided context. If you don't know, honestly say so.

*** CRITICAL LANGUAGE RULES ***
The context provided is in Nepali. However, you MUST reply in the EXACT SAME LANGUAGE and SCRIPT as the user's question. You must translate the information from the context if necessary:
1. If user asks in ENGLISH -> Reply ENTIRELY in PURE ENGLISH (translate context to English).
2. If user asks in NEPALI (Devanagari) -> Reply ENTIRELY in PURE NEPALI (Devanagari).
3. If user asks in ROMANIZED NEPALI -> Reply ENTIRELY in ROMANIZED NEPALI (translate context to Romanized Nepali).

*** ANSWER FORMAT ***
You must use this exact structure, translated into the language you are responding in. Do NOT output markdown headers like ###, just use bold text:

**Direct Answer:** 
(2-3 sentences here)

**Detailed Explanation:**
(Simple language explanation here)

**Impact on Citizens:**
(How it affects people here)

**Source:** [section title, page number]

Do not repeat the context or questions, just give the final answer in the format above.
"""


def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    """
    Build a chat-completion message list for the Groq API
    with the Mr. Wagle persona.

    Args:
        query:  The user's question.
        chunks: Retrieved context chunks with text, section_title,
                page_number, and ministry fields.

    Returns:
        List of message dicts for the Groq chat API.
    """
    # Format the context chunks
    context_parts = []
    for i, c in enumerate(chunks, 1):
        part = (
            f"[Source {i}]\n"
            f"Section: {c['section_title']}\n"
            f"Page: {c['page_number']}\n"
        )
        if c.get("ministry"):
            part += f"Ministry: {c['ministry']}\n"
        part += f"Content:\n{_truncate(c['text'])}"
        context_parts.append(part)

    context_block = "\n\n---\n\n".join(context_parts)

    user_message = (
        f"Context:\n\n{context_block}\n\n"
        f"---\n\n"
        f"Question: {query}\n\n"
        f"*** STRICT REMINDER: You MUST reply in the exact SAME LANGUAGE as the Question. If the Question is in English, your entire response MUST be translated into English. Do not output Nepali if the Question is English. ***"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


if __name__ == "__main__":
    sample_chunks = [
        {
            "text": "शिक्षा मन्त्रालयलाई रु. ५० अर्ब विनियोजन गरिएको छ।",
            "section_title": "शिक्षा बजेट",
            "page_number": 12,
            "ministry": "शिक्षा मन्त्रालय",
        }
    ]
    messages = build_prompt("शिक्षा बजेट कति हो?", sample_chunks)
    for msg in messages:
        print(f"[{msg['role']}]\n{msg['content'][:400]}\n")
