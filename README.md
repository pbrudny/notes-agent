# notes-agent

An AI-powered note-taking agent built with FastAPI, LangGraph, SQLAlchemy, and Neon PostgreSQL.

Chat naturally to save and retrieve notes — the agent decides which tool to call based on your message. All conversations are traced in LangSmith.

## Stack

- **FastAPI** — HTTP API + static frontend
- **LangGraph** — ReAct agent loop
- **SQLAlchemy 2** — ORM for PostgreSQL
- **Neon** — serverless PostgreSQL
- **LangSmith** — LLM tracing and observability
- **uv** — dependency management

## Project structure

```
app/
  main.py       # FastAPI app, endpoints, lifespan
  database.py   # SQLAlchemy engine and session
  models.py     # Note ORM model
  agent.py      # LangGraph agent and tools
static/
  index.html    # Chat UI (vanilla JS)
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Chat UI |
| GET | `/health` | Health check |
| POST | `/chat` | Chat with the agent |
| GET | `/notes` | List all notes |
| GET | `/docs` | Swagger UI |

## Example chat messages

```
"Save a note: LangGraph uses nodes and edges to define agent flows"
"What do I have saved about LangGraph?"
"List my recent notes"
"Save a note titled 'Neon tips' with content: always use connection pooling in serverless"
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key |
| `LANGSMITH_API_KEY` | LangSmith personal access token |
| `LANGSMITH_TRACING` | Set to `true` to enable tracing |
| `LANGSMITH_PROJECT` | LangSmith project name (default: `notes-agent`) |

## Run locally

```bash
uv sync
export DATABASE_URL="your-neon-connection-string"
export OPENAI_API_KEY="your-openai-key"
export LANGSMITH_API_KEY="your-langsmith-key"
export LANGSMITH_TRACING=true
uv run uvicorn app.main:app --reload
```

## Lint

```bash
uv run --group dev ruff check --fix .
uv run --group dev ruff format .
```

## Deploy on Coolify

1. Connect this repo in Coolify → New Resource → Public Repository
2. Build pack: **Dockerfile**
3. Port: **8000**
4. Add environment variables (see table above)
5. Disable **Force HTTPS** in Advanced settings (Cloudflare handles TLS)
6. Leave Port Mappings empty (Traefik routes internally)
7. Deploy
