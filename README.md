# 🏛️ AarthaSandhan (अर्थसन्धान)

**Nepal Budget Document RAG System** — Retrieval-Augmented Generation app for querying Nepal's budget documents in Nepali and English.

## Features

- 📄 **PDF Extraction** — Extracts text from Nepali budget PDFs with ZWJ/ZWNJ character cleaning
- ✂️ **Smart Chunking** — Splits by Devanagari section headings and budget keywords
- 🧠 **Multilingual Embeddings** — Uses `paraphrase-multilingual-MiniLM-L12-v2` for Nepali text
- 🔍 **Semantic Search** — ChromaDB vector store with cosine similarity
- 💬 **RAG Answers** — Groq API (LLaMA 3.1) generates grounded, cited answers
- 🌐 **Bilingual** — Responds in the same language as your query (Nepali or English)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API key

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build the index (one-time)

```bash
python index.py
```

This runs: **extract → chunk → embed** and saves the vector store to `index/chroma_db/`.

### 4. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
AarthaSandhan/
├── data/budget_82-83.pdf        # Nepali budget PDF
├── index/chroma_db/             # Persisted ChromaDB (built locally)
├── src/
│   ├── extract.py               # PDF text extraction + cleaning
│   ├── chunk.py                 # Semantic chunking
│   ├── embed.py                 # Embedding + ChromaDB storage
│   ├── retrieve.py              # Query retrieval
│   ├── prompt.py                # RAG prompt builder
│   └── answer.py                # Groq API caller
├── app.py                       # Streamlit UI
├── index.py                     # Indexing pipeline
└── requirements.txt
```

## Deployment (Streamlit Cloud)

1. Push the repo to GitHub (including `index/chroma_db/`)
2. Add `GROQ_API_KEY` in **Streamlit Cloud → Secrets**
3. The app only runs the query pipeline — no indexing needed on cloud

## Tech Stack

| Component | Technology |
|-----------|-----------|
| PDF Extraction | pdfplumber |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Vector Store | ChromaDB |
| LLM | Groq (llama-3.1-8b-instant) |
| UI | Streamlit |