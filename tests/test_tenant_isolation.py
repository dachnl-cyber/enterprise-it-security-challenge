from .conftest import login

def test_cross_tenant_profile_access_blocked_for_employee(client):
    login(client, "alice")
    response = client.get("/profiles/tenant-b-user-1")
    assert response.status_code == 403
