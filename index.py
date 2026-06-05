"""
index.py — Run the full indexing pipeline: extract → chunk → embed.

This should be run ONCE locally to build the ChromaDB index.
The resulting index/chroma_db/ directory is committed to GitHub
so that Streamlit Cloud can use it directly without re-indexing.
"""

import os
import sys
import time

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from src.extract import extract_pages
from src.chunk import chunk_pages
from src.embed import embed_and_store


PDF_PATH = os.path.join("data", "budget_82-83.pdf")


def main():
    print("=" * 60)
    print("  AarthaSandhan — Indexing Pipeline")
    print("=" * 60)

    # ── Step 1: Extract ────────────────────────────────────────
    print("\n📄 Step 1/3: Extracting text from PDF …")
    t0 = time.time()
    pages = extract_pages(PDF_PATH)
    elapsed = time.time() - t0
    print(f"  ✅ Extracted {len(pages)} pages in {elapsed:.1f}s")

    if not pages:
        print("  ❌ No pages extracted. Check the PDF path.")
        sys.exit(1)

    # ── Step 2: Chunk ──────────────────────────────────────────
    print("\n✂️  Step 2/3: Chunking into semantic segments …")
    t0 = time.time()
    chunks = chunk_pages(pages)
    elapsed = time.time() - t0
    print(f"  ✅ Created {len(chunks)} chunks in {elapsed:.1f}s")

    # Print chunk statistics
    word_counts = [len(c["text"].split()) for c in chunks]
    print(f"  📊 Words per chunk — min: {min(word_counts)}, "
          f"max: {max(word_counts)}, avg: {sum(word_counts)//len(word_counts)}")

    # ── Step 3: Embed & Store ──────────────────────────────────
    print("\n🧠 Step 3/3: Embedding and storing in ChromaDB …")
    t0 = time.time()
    embed_and_store(chunks)
    elapsed = time.time() - t0
    print(f"  ✅ Indexing complete in {elapsed:.1f}s")

    print("\n" + "=" * 60)
    print("  ✅ Done! Index saved to index/chroma_db/")
    print("  You can now run: streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
