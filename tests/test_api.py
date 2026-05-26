from unittest.mock import MagicMock, patch

from app.database import get_db
from app.models import Note


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_notes_empty(client):
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_notes_list(client):
    with get_db() as db:
        db.add(Note(title="First", content="Hello"))
        db.add(Note(title="Second", content="World"))

    resp = client.get("/notes")
    assert resp.status_code == 200
    notes = resp.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "Second"  # desc order


def test_chat(client):
    with patch("app.main.agent") as mock_agent:
        mock_msg = MagicMock()
        mock_msg.content = "Note saved!"
        mock_agent.invoke.return_value = {"messages": [mock_msg]}

        resp = client.post("/chat", json={"message": "save a note"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "Note saved!"
    assert data["session_id"] == "default"


def test_chat_custom_session(client):
    with patch("app.main.agent") as mock_agent:
        mock_msg = MagicMock()
        mock_msg.content = "Done"
        mock_agent.invoke.return_value = {"messages": [mock_msg]}

        resp = client.post("/chat", json={"message": "hello", "session_id": "user-123"})

    assert resp.status_code == 200
    assert resp.json()["session_id"] == "user-123"


def test_chat_agent_error(client):
    with patch("app.main.agent") as mock_agent:
        mock_agent.invoke.side_effect = RuntimeError("OpenAI timeout")

        resp = client.post("/chat", json={"message": "hello"})

    assert resp.status_code == 500
    assert "OpenAI timeout" in resp.json()["detail"]
