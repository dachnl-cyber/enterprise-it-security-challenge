import os
import tempfile
import pytest

from app.app import create_app
from app.seed import seed_data
from app.db import initialize_schema

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update(
        TESTING=True,
        DATABASE=db_path,
        SECRET_KEY="test-secret",
        UPLOAD_FOLDER="uploads",
    )

    with app.app_context():
        initialize_schema()
        seed_data()

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username, password="password123"):
    return client.post("/login", json={"username": username, "password": password})
