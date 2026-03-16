from .conftest import login

def test_same_tenant_profile_access_allowed(client):
    login(client, "alice")
    response = client.get("/profiles/tenant-a-user-1")
    assert response.status_code == 200

def test_profile_lookup_requires_login(client):
    response = client.get("/profiles/tenant-a-user-1")
    assert response.status_code == 401
