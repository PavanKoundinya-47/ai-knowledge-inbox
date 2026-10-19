# AI Knowledge Inbox

A full-stack knowledge inbox: save text notes or URLs, index content with embeddings, then ask questions answered from retrieved context with source citations.

## Stack
- React + Vite frontend
- Python + FastAPI backend
- PostgreSQL + pgvector
- OpenAI embeddings and chat completion API
- Docker Compose for local PostgreSQL

## Run locally

1. Install Docker, Python 3.11+, Node.js 20+, and obtain an OpenAI API key.
2. From the project root:
   ```bash
   docker compose up -d db
   cp .env.example .env
   ```
   Set `OPENAI_API_KEY` in `.env`.
3. Backend:
   ```bash
   cd backend
   python -m venv .venv
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
4. In a second terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
5. Open http://localhost:5173. API docs: http://localhost:8000/docs.

## API
- `POST /ingest`: `{"type":"note","content":"..."}`
- `POST /ingest`: `{"type":"url","url":"https://example.com"}`
- `GET /items`: list items and processing statuses
- `POST /query`: `{"question":"What did I save about ...?","top_k":5}`

Ingestion returns `202 Accepted`; poll `GET /items` until status is `ready` or `failed`.

## Design decisions and tradeoffs
- **PostgreSQL + pgvector:** durable metadata/content and vectors in one service; avoids a separate vector database.
- **Character chunks with overlap:** simple, dependency-free baseline. Production should use token-aware and structure-aware splitting.
- **Exact cosine-distance search:** appropriate for a small assessment corpus. Benchmark HNSW/IVFFlat before adding index complexity.
- **FastAPI background tasks:** demonstrate async workflows with minimal infrastructure, but tasks are not durable across process crashes. Production should use a durable queue, retries, and idempotency.
- **Single-user scope:** no auth, as permitted by the brief. Add authentication and tenant isolation before multi-user deployment.
- **Grounded RAG:** the LLM receives retrieved context and is instructed to abstain when context is insufficient. Citation metadata is built from retrieved database records, not model-generated claims.

## Error handling and security
- Pydantic request validation, useful HTTP errors, structured request logs.
- URL fetching blocks non-public IP addresses, checks redirects, limits response size, and has timeouts. This reduces SSRF exposure but is not a replacement for production egress controls; DNS rebinding and complex network setups need stronger defenses.
- Do not commit `.env` or API keys. URL content is untrusted; the prompt explicitly treats it as data, not instructions.

## Tests
From `backend/`: `pytest`. Unit tests cover chunking and request validation. Full integration tests require PostgreSQL and valid OpenAI credentials.

## What breaks at scale
Use durable workers, auth/tenant isolation, migrations, connection-pool tuning, vector indexes after benchmarks, deduplication, richer document extraction, rate limits, observability, RAG evaluation, cost tracking, and hardened URL egress controls.

## Demo
1. Save a note such as “Our service uses FastAPI, PostgreSQL, and async background jobs.”
2. Wait until it is `ready`.
3. Ask “Which technologies does the service use?”
4. Inspect returned source snippets and verify that unrelated questions do not receive fabricated answers.
