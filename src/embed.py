"""
embed.py — Embed chunks using paraphrase-multilingual-MiniLM-L12-v2
and persist them to ChromaDB at index/chroma_db/.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_PATH = os.path.join("index", "chroma_db")
COLLECTION_NAME = "budget_chunks"


def get_model() -> SentenceTransformer:
    """Load the multilingual sentence transformer model."""
    return SentenceTransformer(MODEL_NAME)


def embed_and_store(chunks: list[dict], chroma_path: str = CHROMA_PATH) -> None:
    """
    Embed all chunks and store them in a persisted ChromaDB collection.

    Each chunk dict must have: text, section_title, page_number, ministry.
    """
    model = get_model()

    # Extract texts for batch embedding
    texts = [c["text"] for c in chunks]
    print(f"  ⏳ Embedding {len(texts)} chunks …")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    embeddings_list = [emb.tolist() for emb in embeddings]

    # Initialise ChromaDB with persistent storage
    client = chromadb.PersistentClient(path=chroma_path)

    # Delete existing collection if it exists (fresh build)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # Collection doesn't exist yet — that's fine

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Prepare IDs and metadata
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "section_title": c["section_title"],
            "page_number": c["page_number"],
            "ministry": c["ministry"],
        }
        for c in chunks
    ]

    # Add in batches (ChromaDB supports up to ~41666 per batch)
    BATCH_SIZE = 500
    for start in range(0, len(chunks), BATCH_SIZE):
        end = min(start + BATCH_SIZE, len(chunks))
        collection.add(
            ids=ids[start:end],
            embeddings=embeddings_list[start:end],
            documents=texts[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"  ✅ Stored {collection.count()} chunks in ChromaDB at {chroma_path}")


if __name__ == "__main__":
    from extract import extract_pages
    from chunk import chunk_pages

    pages = extract_pages("data/budget_82-83.pdf")
    chunks = chunk_pages(pages)
    embed_and_store(chunks)
