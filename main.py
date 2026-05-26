import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

DATABASE_URL = os.environ["DATABASE_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Notes Agent", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)


@tool
def save_note(title: str, content: str) -> str:
    """Save a note with a title and content to the database."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id",
                (title, content),
            )
            note_id = cur.fetchone()[0]
        conn.commit()
    return f"Note saved with ID {note_id}."


@tool
def search_notes(query: str) -> str:
    """Search notes by keyword in title or content."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, content, created_at
                FROM notes
                WHERE title ILIKE %s OR content ILIKE %s
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (f"%{query}%", f"%{query}%"),
            )
            rows = cur.fetchall()
    if not rows:
        return "No notes found matching that query."
    return "\n\n".join(
        f"[{r[0]}] {r[1]} ({r[3].strftime('%Y-%m-%d')})\n{r[2]}" for r in rows
    )


@tool
def list_notes() -> str:
    """List the 10 most recent notes."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, created_at FROM notes ORDER BY created_at DESC LIMIT 10"
            )
            rows = cur.fetchall()
    if not rows:
        return "No notes saved yet."
    return "\n".join(f"[{r[0]}] {r[1]} — {r[2].strftime('%Y-%m-%d %H:%M')}" for r in rows)


agent = create_react_agent(llm, tools=[save_note, search_notes, list_notes])


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = agent.invoke({"messages": [HumanMessage(content=req.message)]})
        reply = result["messages"][-1].content
        return ChatResponse(reply=reply, session_id=req.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notes")
def get_notes():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
    return [
        {"id": r[0], "title": r[1], "content": r[2], "created_at": r[3]}
        for r in rows
    ]
