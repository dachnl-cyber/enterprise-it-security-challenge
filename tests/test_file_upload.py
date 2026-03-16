import io
from .conftest import login

def test_upload_requires_authentication(client):
    data = {"file": (io.BytesIO(b"hello"), "test.txt")}
    response = client.post("/uploads", data=data, content_type="multipart/form-data")
    assert response.status_code == 401

def test_upload_allows_safe_extension(client):
    login(client, "alice")
    data = {"file": (io.BytesIO(b"hello"), "evidence.txt")}
    response = client.post("/uploads", data=data, content_type="multipart/form-data")
    assert response.status_code == 201
