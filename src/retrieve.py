"""
retrieve.py — Query ChromaDB for the most relevant chunks given a user query.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

from src.embed import MODEL_NAME, CHROMA_PATH, COLLECTION_NAME


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the user query and retrieve the top-k most similar chunks
    from ChromaDB.

    Returns a list of dicts:
        [{"text": str, "section_title": str, "page_number": int,
          "ministry": str, "score": float}, ...]

    Score is a *similarity* score (higher = more similar), derived
    from ChromaDB's distance (cosine distance).
    """
    # Load the same model used for indexing
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([query])[0].tolist()

    # Connect to the persisted ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)

    # Query
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Build response — convert cosine distance to similarity score
    chunks = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        similarity = 1.0 - distance  # cosine: similarity = 1 - distance
        chunks.append({
            "text": results["documents"][0][i],
            "section_title": results["metadatas"][0][i].get("section_title", ""),
            "page_number": results["metadatas"][0][i].get("page_number", 0),
            "ministry": results["metadatas"][0][i].get("ministry", ""),
            "score": round(similarity, 4),
        })

    return chunks


if __name__ == "__main__":
    test_query = "शिक्षा मन्त्रालयको बजेट कति हो?"
    results = retrieve(test_query)
    print(f"Query: {test_query}")
    print(f"Found {len(results)} results:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] Score: {r['score']:.4f}  |  Page: {r['page_number']}  |  Section: {r['section_title'][:60]}")
