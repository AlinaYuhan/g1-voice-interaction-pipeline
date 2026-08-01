# XJTLU Intelligent Assistant — Local RAG Knowledge Base

[English](README.md) | [中文](README.zh-CN.md)

A local retrieval-augmented generation (RAG) system based on a Xi'an Jiaotong-Liverpool University knowledge base. It uses the DeepSeek API for intelligent question answering and supports assistant identity switching and conversation memory.

> This is an optional experimental backend. It is not connected to or started by the main voice pipeline by default; the supported default reply backend calls DeepSeek directly. See [Optional XJTLU RAG](../docs/OPTIONAL_RAG.md) for integration details.

## Technical architecture

| Function | Provider | Description |
|----------|----------|-------------|
| Chat generation | DeepSeek API | `deepseek-v4-pro` model |
| Vector embeddings | Ollama (local) | `nomic-embed-text` model |

## Pipeline

```
User message → identity inference → profile extraction → small-talk detection
                                                       │
                            ┌──────────────────────────┼──────────────────────────┐
                            ▼                          ▼                          ▼
                    RAG vector search          FAQ keyword lookup        programme lookup
                            │                          │                          │
                            └──────────────────────────┼──────────────────────────┘
                                                       ▼
                              Prompt assembly (identity + profile + history + knowledge base)
                                                       │
                                                       ▼
                                      DeepSeek API (deepseek-v4-pro)
                                                       │
                                                       ▼
                              Answer truncation (150 Chinese characters) + source list
                                                       │
                                                       ▼
                    JSON: { answer, identity, profile, sources, action, timing }
```

## Directory structure

```
xjtlu-rag-system/
├── app.py                 # FastAPI application (/chat, /health, /profile)
├── chat_engine.py         # Identity, retrieval, prompt, action, and timing orchestration
├── vector_store.py        # SQLite vector search (cosine similarity)
├── memory_store.py        # SQLite conversation memory (profile + history)
├── ingest.py              # Knowledge-base vectorization script
├── knowledge_extract.py   # Knowledge extractor (6 source categories)
├── ollama_client.py       # DeepSeek and Ollama client
├── rag_config.py          # Environment-variable configuration loader
├── test_connection.py     # Connection test utility
├── ros_bridge.py          # ROS2 bridge (subscribes /audio_msg, publishes /xjtlu_reply)
├── requirements.txt       # Reuses the repository-root LLM requirements
├── xjtlu_knowledge.db     # Tracked source knowledge database
├── rag_index.db           # Tracked vector index database; rebuilt by ingest.py
├── chat_memory.db         # Generated local conversation memory database
├── start.bat              # Windows batch launcher
├── start.ps1              # One-command Windows launcher
├── start_ros_bridge.ps1   # ROS2 bridge launcher
└── static/                # Frontend static files
    ├── index.html
    ├── main.js
    └── style.css
```

`xjtlu_knowledge.db` is the Git-tracked source knowledge database included with the repository and read during ingestion. `rag_index.db` is also tracked and stores the generated vectors used for retrieval; `python ingest.py --reset` rebuilds it. `chat_memory.db` contains runtime user profiles and conversation history; it is generated local state, is not Git-tracked, and is not required by the default main pipeline.

## Quick start

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

`xjtlu-rag-system/requirements.txt` reuses the repository-root `requirements-llm.txt` rather than duplicating version pins. Its complete contents are:

```
-r ../requirements-llm.txt
```

### Step 2: Install Ollama and configure the embedding model

1. Download and install [Ollama for Windows](https://ollama.com/download).
2. Download the embedding model:

```powershell
ollama pull nomic-embed-text
```

### Step 3: Configure

```powershell
notepad .env
```

`rag_config.py` first reads a local `.env` file when one exists, while environment variables already set in the process take precedence. The repository does not currently include an `.env.example` template, so create `.env` manually and do not commit it.

The current `start.ps1` requires `.env`. If the file is absent, the script attempts to copy the missing `.env.example` and cannot proceed. Create `.env` manually before using `start.ps1`, or start Uvicorn manually as shown in Step 6.

Key configuration values:

```ini
CHAT_PROVIDER=openai
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-your-deepseek-api-key
CHAT_MODEL=deepseek-v4-pro

EMBED_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
EMBED_MODEL=nomic-embed-text
```

### Step 4: Test connectivity

```bash
python test_connection.py
```

### Step 5: Build the vector index (first run)

```bash
python ingest.py --reset
```

### Step 6: Start the service

```powershell
.\start.ps1
# Or start manually:
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Open **http://127.0.0.1:8000**.

---

## Features

- **Intelligent Q&A:** accurate answers grounded in the XJTLU knowledge base.
- **Identity switching:** automatic selection among admissions adviser, academic adviser, and campus assistant.
- **Conversation memory:** automatically remembers the user's name, programme interests, language preference, and conversation context.
- **Natural small talk:** casual conversation is not forced to cite the knowledge base.
- **Source references:** answers include links to knowledge-base sources.
- **DeepSeek-powered:** high-quality response generation through the DeepSeek API.

---

## Identity switching

| Identity | Trigger keywords | Response style |
|----------|------------------|----------------|
| Campus assistant | (default) | Natural, friendly, concise |
| Admissions adviser | "招生顾问", or "招生" + "身份" | Clear, cautious, aimed at prospective students and parents |
| Academic adviser | "学术导师", or "导师" + "身份" | Professional, focused on course pathways and academic development |

---

## API

### POST /chat

```json
// Request
{
  "session_id": "student-1",
  "message": "What programmes does XJTLU offer? Please answer in English."
}

// Response
{
  "answer": "XJTLU offers...",
  "identity": "校园助手",
  "profile": {
    "name": "Alex",
    "assistant_identity": "校园助手"
  },
  "sources": [
    {
      "title": "Programme list",
      "url": "https://...",
      "category": "programmes",
      "score": 0.8542
    }
  ],
  "action": {
    "label": "举右手",
    "official_name": "right hand up",
    "action_id": 23,
    "score": 0.92,
    "backend": "deepseek",
    "reason": "A routine campus-information explanation."
  },
  "timing": {
    "rag_embed_sec": 0.083,
    "rag_search_sec": 0.012,
    "llm_sec": 0.731,
    "total_sec": 0.826
  }
}
```

The response fields are:

- `answer`: response text, limited to 150 Chinese characters by default.
- `identity`: one of the runtime assistant identity strings, such as `校园助手`.
- `profile`: a string-to-string map containing known user attributes such as `name`, `major_interest`, `language`, and `assistant_identity` when available.
- `sources`: a list of objects with `title`, `url`, `category`, and numeric `score` fields.
- `action`: an object with string fields `label`, `official_name`, `backend`, and `reason`, integer `action_id`, and numeric `score` clamped to 0–1.
- `timing`: an object of elapsed seconds with numeric `rag_embed_sec`, `rag_search_sec`, `llm_sec`, and `total_sec` fields.

### GET /health

```json
{
  "status": "ok",
  "rag_db": "./rag_index.db",
  "memory_db": "./chat_memory.db",
  "embed_model": "nomic-embed-text",
  "chat_model": "deepseek-v4-pro"
}
```

### GET /profile/{session_id}

Returns the user profile and the 50 most recent messages for the specified session.

### GET /docs

Automatically generated interactive FastAPI documentation (Swagger UI).

---

## Configuration reference

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAT_PROVIDER` | Chat API type | `openai` |
| `EMBED_PROVIDER` | Embedding API type | `ollama` |
| `OPENAI_BASE_URL` | DeepSeek API URL | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | DeepSeek API key | Required |
| `CHAT_MODEL` | Chat model name | `deepseek-v4-pro` |
| `OLLAMA_BASE_URL` | Ollama service URL | `http://127.0.0.1:11434` |
| `EMBED_MODEL` | Embedding model name | `nomic-embed-text` |
| `TOP_K` | Number of RAG results | `10` |
| `SIMILARITY_THRESHOLD` | Similarity threshold (0–1) | `0.35` |
| `ANSWER_MAX_CHARS` | Maximum response length in Chinese characters | `150` |

---

## Troubleshooting

**Q: What should I do if I see "connection failed"?**

1. Confirm that the Ollama service is running.
2. Confirm that `ollama pull nomic-embed-text` has been run.
3. Check that `OPENAI_API_KEY` in `.env` is valid.
4. Run `python test_connection.py` for detailed error information.

**Q: What should I do if answer quality is poor?**

1. Rebuild the index: `python ingest.py --reset`.
2. Adjust `SIMILARITY_THRESHOLD` (raise it to 0.45 for higher precision, or lower it to 0.25 to return more references).

---

## Technology stack

- **Backend:** FastAPI + Uvicorn
- **Chat model:** DeepSeek API (`deepseek-v4-pro`)
- **Vector embeddings:** Ollama (`nomic-embed-text`, running locally)
- **Vector storage:** SQLite + NumPy (cosine similarity)
- **Conversation memory:** SQLite
- **Frontend:** Vanilla HTML/CSS/JavaScript

---

## License

MIT License
