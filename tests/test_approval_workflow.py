from .conftest import login

def test_employee_can_create_approval_request(client):
    login(client, "alice")
    response = client.post(
        "/approvals",
        json={"target_system": "finance-share", "requested_role": "read_only"},
    )
    assert response.status_code == 201

def test_manager_can_approve_request(client):
    login(client, "mary")
    response = client.post("/approvals/1/approve")
    assert response.status_code == 200
