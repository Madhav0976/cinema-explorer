import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Reusable TestClient for FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """SQLAlchemy session for direct database verification."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

