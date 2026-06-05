"""
answer.py — Call the Groq API to generate an answer from the RAG prompt.
"""

import os
from groq import Groq


MODEL = "llama-3.1-8b-instant"


def get_answer(messages: list[dict], api_key: str | None = None) -> str:
    """
    Send the prompt messages to Groq and return the generated answer.

    Args:
        messages: Chat-completion message list from prompt.build_prompt().
        api_key:  Groq API key. Falls back to GROQ_API_KEY env var.

    Returns:
        The model's response text.
    """
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY not found. Set it in your .env file, "
            "environment variable, or pass it directly."
        )

    client = Groq(api_key=key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,       # Low temperature for factual answers
        max_tokens=1024,       # Keep under Groq free-tier TPM limits
        top_p=0.9,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in Nepali."},
    ]
    print(get_answer(test_messages))
