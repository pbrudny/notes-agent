import os

# Must be set before any app module is imported
os.environ.setdefault("DATABASE_URL", "sqlite:///./tests/test.db")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("LANGSMITH_API_KEY", "ls-test")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(reset_db):
    with TestClient(app) as c:
        yield c
