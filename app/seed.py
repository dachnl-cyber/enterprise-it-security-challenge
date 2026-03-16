from .db import get_db, initialize_schema

def seed_data():
    initialize_schema()
    db = get_db()

    tenant_count = db.execute("SELECT COUNT(*) AS c FROM tenants").fetchone()["c"]
    if tenant_count > 0:
        return

    db.execute("INSERT INTO tenants (name) VALUES (?)", ("Tenant A",))
    db.execute("INSERT INTO tenants (name) VALUES (?)", ("Tenant B",))

    users = [
        ("alice", "password123", "employee", 1, "Alice Employee", "alice@tenant-a.example"),
        ("mary", "password123", "manager", 1, "Mary Manager", "mary@tenant-a.example"),
        ("ian", "password123", "it_admin", 1, "Ian IT", "ian@tenant-a.example"),
        ("claire", "password123", "compliance_admin", 1, "Claire Compliance", "claire@tenant-a.example"),
        ("bob", "password123", "employee", 2, "Bob Employee", "bob@tenant-b.example"),
        ("brenda", "password123", "manager", 2, "Brenda Manager", "brenda@tenant-b.example"),
    ]

    db.executemany(
        """
        INSERT INTO users (username, password, role, tenant_id, full_name, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        users,
    )

    profiles = [
        (1, "tenant-a-user-1", "Engineer", "Infrastructure", 1),
        (2, "tenant-a-user-2", "Manager", "Operations", 1),
        (5, "tenant-b-user-1", "Analyst", "Compliance", 2),
        (6, "tenant-b-user-2", "Manager", "Finance", 2),
    ]

    db.executemany(
        """
        INSERT INTO profiles (user_id, employee_id, title, department, tenant_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        profiles,
    )

    tickets = [
        ("Laptop issue", "Cannot connect to VPN", 1, 1, "open"),
        ("Admin request", "Need elevated access to payroll export", 2, 1, "open"),
        ("Access review", "Need access to finance share", 5, 2, "open"),
    ]

    db.executemany(
        """
        INSERT INTO tickets (title, description, created_by, tenant_id, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        tickets,
    )

    approvals = [
        (1, "finance-share", "read_only", "Quarterly reconciliation support", "pending", None, 1),
        (5, "payroll-admin", "elevated", "Urgent support coverage", "pending", None, 2),
    ]

    db.executemany(
        """
        INSERT INTO approval_requests
        (requester_id, target_system, requested_role, justification, status, approved_by, tenant_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        approvals,
    )

    audit_events = [
        (1, "seed_login", "seeded login event for alice", 1),
        (5, "seed_login", "seeded login event for bob", 2),
    ]

    db.executemany(
        """
        INSERT INTO audit_events (actor_user_id, action, details, tenant_id)
        VALUES (?, ?, ?, ?)
        """,
        audit_events,
    )

    db.commit()
