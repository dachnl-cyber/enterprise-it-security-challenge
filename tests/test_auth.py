from .conftest import login

def test_login_required_for_dashboard(client):
    response = client.get("/dashboard")
    assert response.status_code == 401

def test_valid_login_works(client):
    response = login(client, "alice")
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["username"] == "alice"
