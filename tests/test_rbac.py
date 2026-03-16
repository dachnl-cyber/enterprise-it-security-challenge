from .conftest import login

def test_employee_cannot_access_admin_export(client):
    login(client, "alice")
    response = client.get("/admin/audit-export")
    assert response.status_code == 403

def test_it_admin_can_access_admin_export(client):
    login(client, "ian")
    response = client.get("/admin/audit-export")
    assert response.status_code == 200
