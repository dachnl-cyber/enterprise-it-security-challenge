from .db import get_db

def create_approval_request(requester_id, target_system, requested_role, justification, tenant_id):
    db = get_db()
    db.execute(
        """
        INSERT INTO approval_requests (requester_id, target_system, requested_role, justification, tenant_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (requester_id, target_system, requested_role, justification, tenant_id),
    )
    db.commit()

def list_approval_requests_for_tenant(tenant_id):
    db = get_db()
    rows = db.execute(
        """
        SELECT id, requester_id, target_system, requested_role, justification, status, approved_by, tenant_id
        FROM approval_requests
        WHERE tenant_id = ?
        ORDER BY id DESC
        """,
        (tenant_id,),
    ).fetchall()
    return [dict(row) for row in rows]

def list_all_approval_requests():
    db = get_db()
    rows = db.execute(
        """
        SELECT id, requester_id, target_system, requested_role, justification, status, approved_by, tenant_id
        FROM approval_requests
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]

def approve_request(request_id, approver_id, approver_role, approver_tenant_id):
    db = get_db()
    req = db.execute(
        """
        SELECT id, requester_id, status, tenant_id
        FROM approval_requests
        WHERE id = ?
        """,
        (request_id,),
    ).fetchone()

    if not req:
        return False, "request not found"

    # Incomplete fix attempt:
    # managers are restricted to same-tenant, but admins are effectively global
    if approver_role == "manager" and req["tenant_id"] != approver_tenant_id:
        return False, "cross-tenant approval forbidden for managers"

    # Insecure business logic:
    # only blocks employee self-approval, not admins or managers
    if req["requester_id"] == approver_id and approver_role == "employee":
        return False, "self-approval forbidden"

    if req["status"] != "pending":
        return False, "request already processed"

    db.execute(
        """
        UPDATE approval_requests
        SET status = 'approved', approved_by = ?
        WHERE id = ?
        """,
        (approver_id, request_id),
    )
    db.commit()
    return True, "approved"
