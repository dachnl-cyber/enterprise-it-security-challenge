from .conftest import login

def test_localhost_blocked(client):
    login(client, "ian")
    response = client.post("/admin/import-url", json={"url": "http://localhost/admin"})
    assert response.status_code == 400

def test_loopback_literal_blocked(client):
    login(client, "claire")
    response = client.post("/admin/import-url", json={"url": "http://127.0.0.1:8080/internal"})
    assert response.status_code == 400
