import os

os.environ["DEMO_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
