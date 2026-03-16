from .conftest import login

def test_audit_export_requires_authorized_role(client):
    login(client, "alice")
    response = client.get("/admin/audit-export")
    assert response.status_code == 403

def test_audit_export_returns_json_for_admin(client):
    login(client, "ian")
    response = client.get("/admin/audit-export")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
