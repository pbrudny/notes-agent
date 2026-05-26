# notes-agent

An AI-powered note-taking agent built with FastAPI, LangGraph, and Neon PostgreSQL.

Chat naturally to save and retrieve notes — the agent decides which tool to call based on your message.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
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

## Run locally

```bash
pip install -r requirements.txt
export DATABASE_URL="your-neon-connection-string"
export OPENAI_API_KEY="your-openai-key"
uvicorn main:app --reload
```

## Deploy on Coolify

1. Connect this repo in Coolify → New Resource → Public Repository
2. Build pack: **Dockerfile**
3. Port: **8000**
4. Add environment variables: `DATABASE_URL` and `OPENAI_API_KEY`
5. Assign your team subdomain
6. Deploy
