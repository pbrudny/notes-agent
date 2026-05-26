import os

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.database import get_db
from app.models import Note

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])


@tool
def save_note(title: str, content: str) -> str:
    """Save a note with a title and content to the database."""
    with get_db() as db:
        note = Note(title=title, content=content)
        db.add(note)
        db.flush()
        note_id = note.id
    return f"Note saved with ID {note_id}."


@tool
def search_notes(query: str) -> str:
    """Search notes by keyword in title or content."""
    with get_db() as db:
        notes = (
            db.query(Note)
            .filter(Note.title.ilike(f"%{query}%") | Note.content.ilike(f"%{query}%"))
            .order_by(Note.created_at.desc())
            .limit(5)
            .all()
        )
    if not notes:
        return "No notes found matching that query."
    return "\n\n".join(
        f"[{n.id}] {n.title} ({n.created_at.strftime('%Y-%m-%d')})\n{n.content}" for n in notes
    )


@tool
def list_notes() -> str:
    """List the 10 most recent notes."""
    with get_db() as db:
        notes = db.query(Note).order_by(Note.created_at.desc()).limit(10).all()
    if not notes:
        return "No notes saved yet."
    return "\n".join(
        f"[{n.id}] {n.title} — {n.created_at.strftime('%Y-%m-%d %H:%M')}" for n in notes
    )


agent = create_react_agent(llm, tools=[save_note, search_notes, list_notes])
