from app.agent import list_notes, save_note, search_notes
from app.database import get_db
from app.models import Note


def test_save_note(reset_db):
    result = save_note.invoke({"title": "Test", "content": "Body"})
    assert "Note saved with ID" in result

    with get_db() as db:
        note = db.query(Note).first()
        assert note.title == "Test"
        assert note.content == "Body"


def test_list_notes_empty(reset_db):
    result = list_notes.invoke({})
    assert result == "No notes saved yet."


def test_list_notes(reset_db):
    with get_db() as db:
        db.add(Note(title="Alpha", content="first"))
        db.add(Note(title="Beta", content="second"))

    result = list_notes.invoke({})
    assert "Alpha" in result
    assert "Beta" in result


def test_search_notes_match(reset_db):
    with get_db() as db:
        db.add(Note(title="Python tips", content="Use list comprehensions"))
        db.add(Note(title="SQL tips", content="Use indexes"))

    result = search_notes.invoke({"query": "Python"})
    assert "Python tips" in result
    assert "SQL tips" not in result


def test_search_notes_no_results(reset_db):
    result = search_notes.invoke({"query": "nonexistent"})
    assert result == "No notes found matching that query."


def test_search_notes_content_match(reset_db):
    with get_db() as db:
        db.add(Note(title="Misc", content="LangGraph is great"))

    result = search_notes.invoke({"query": "LangGraph"})
    assert "Misc" in result
