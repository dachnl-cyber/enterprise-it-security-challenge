from .db import get_db

def log_event(actor_user_id, action, details, tenant_id):
    db = get_db()
    # Incomplete fix: parameterized insert, but still accepts raw user-controlled details.
    db.execute(
        """
        INSERT INTO audit_events (actor_user_id, action, details, tenant_id)
        VALUES (?, ?, ?, ?)
        """,
        (actor_user_id, action, details, tenant_id),
    )
    db.commit()

def fetch_audit_events_for_tenant(tenant_id):
    db = get_db()
    rows = db.execute(
        """
        SELECT id, actor_user_id, action, details, tenant_id, created_at
        FROM audit_events
        WHERE tenant_id = ?
        ORDER BY id DESC
        """,
        (tenant_id,),
    ).fetchall()
    return [dict(row) for row in rows]

def fetch_all_audit_events():
    db = get_db()
    rows = db.execute(
        """
        SELECT id, actor_user_id, action, details, tenant_id, created_at
        FROM audit_events
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]
