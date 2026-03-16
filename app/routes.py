import os
import requests
from flask import request, jsonify, render_template, send_from_directory, current_app
from .auth import authenticate, login_user, logout_user
from .db import get_db
from .utils import require_login, require_role, current_user, weak_tenant_gate
from .audit import log_event, fetch_audit_events_for_tenant, fetch_all_audit_events
from .storage import save_upload, list_uploads_for_tenant, get_upload_by_id
from .approvals import (
    create_approval_request,
    list_approval_requests_for_tenant,
    list_all_approval_requests,
    approve_request,
)

def register_routes(app):
    @app.get("/")
    def index():
        return jsonify({"message": "Enterprise IT Security Challenge app"})

    @app.get("/login")
    def login_page():
        return render_template("login.html")

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or request.form
        username = data.get("username", "")
        password = data.get("password", "")

        user = authenticate(username, password)
        if not user:
            return jsonify({"error": "invalid credentials"}), 401

        login_user(user)
        log_event(user["id"], "login", f"user={user['username']}", user["tenant_id"])
        return jsonify({"message": "logged in", "user": user})

    @app.post("/logout")
    @require_login
    def logout():
        user = current_user()
        log_event(user["id"], "logout", f"user={user['username']}", user["tenant_id"])
        logout_user()
        return jsonify({"message": "logged out"})

    @app.get("/dashboard")
    @require_login
    def dashboard():
        user = current_user()
        return render_template("dashboard.html", user=user)

    @app.get("/profiles/<employee_id>")
    @require_login
    def get_profile(employee_id):
        db = get_db()
        row = db.execute(
            """
            SELECT p.id, p.user_id, p.employee_id, p.title, p.department, p.tenant_id,
                   u.full_name, u.email
            FROM profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

        if not row:
            return jsonify({"error": "profile not found"}), 404

        user = current_user()

        # Insecure: admins bypass tenant boundaries globally
        if not weak_tenant_gate(user, row["tenant_id"]):
            return jsonify({"error": "forbidden"}), 403

        return jsonify(dict(row))

    @app.get("/tickets")
    @require_login
    def list_tickets():
        user = current_user()
        db = get_db()

        tenant_override = request.args.get("tenant_id")
        target_tenant = tenant_override if tenant_override else user["tenant_id"]

        # Insecure: employee can enumerate another tenant if they know the id
        rows = db.execute(
            """
            SELECT id, title, description, created_by, tenant_id, status
            FROM tickets
            WHERE tenant_id = ?
            ORDER BY id DESC
            """,
            (target_tenant,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/tickets")
    @require_login
    def create_ticket():
        user = current_user()
        data = request.get_json(silent=True) or {}
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()

        if not title or not description:
            return jsonify({"error": "title and description required"}), 400

        db = get_db()
        db.execute(
            """
            INSERT INTO tickets (title, description, created_by, tenant_id)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, user["id"], user["tenant_id"]),
        )
        db.commit()

        # Insecure log details: raw title included
        log_event(user["id"], "create_ticket", title, user["tenant_id"])
        return jsonify({"message": "ticket created"}), 201

    @app.get("/approvals")
    @require_login
    def approvals_list():
        user = current_user()

        # Insecure: admins see all tenant approvals
        if user["role"] in {"it_admin", "compliance_admin"}:
            return jsonify(list_all_approval_requests())

        return jsonify(list_approval_requests_for_tenant(user["tenant_id"]))

    @app.post("/approvals")
    @require_login
    def approvals_create():
        user = current_user()
        data = request.get_json(silent=True) or {}
        target_system = data.get("target_system", "").strip()
        requested_role = data.get("requested_role", "").strip()
        justification = data.get("justification", "").strip()

        if not target_system or not requested_role:
            return jsonify({"error": "missing fields"}), 400

        # Insecure: accepts client-provided tenant override
        tenant_id = data.get("tenant_id", user["tenant_id"])

        create_approval_request(
            requester_id=user["id"],
            target_system=target_system,
            requested_role=requested_role,
            justification=justification,
            tenant_id=tenant_id,
        )
        log_event(user["id"], "create_approval_request", target_system, user["tenant_id"])
        return jsonify({"message": "approval request created"}), 201

    @app.post("/approvals/<int:request_id>/approve")
    @require_role("manager", "it_admin", "compliance_admin")
    def approval_approve(request_id):
        user = current_user()
        ok, msg = approve_request(
            request_id,
            user["id"],
            user["role"],
            user["tenant_id"],
        )
        if not ok:
            return jsonify({"error": msg}), 403

        log_event(
            user["id"],
            "approve_request",
            f"request_id={request_id};approved_by={user['username']}",
            user["tenant_id"],
        )
        return jsonify({"message": msg})

    @app.post("/uploads")
    @require_login
    def upload_file():
        user = current_user()
        file_obj = request.files.get("file")
        try:
            stored_filename = save_upload(file_obj, user["id"], user["tenant_id"])
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        log_event(user["id"], "upload_file", stored_filename, user["tenant_id"])
        return jsonify({"message": "uploaded", "stored_filename": stored_filename}), 201

    @app.get("/uploads")
    @require_login
    def uploads_list():
        user = current_user()

        # Insecure: cross-tenant listing for admins
        tenant_id = request.args.get("tenant_id", user["tenant_id"])
        if user["role"] in {"it_admin", "compliance_admin"}:
            return jsonify(list_uploads_for_tenant(tenant_id))

        return jsonify(list_uploads_for_tenant(user["tenant_id"]))

    @app.get("/uploads/<int:upload_id>/download")
    @require_login
    def download_upload(upload_id):
        upload = get_upload_by_id(upload_id)
        if not upload:
            return jsonify({"error": "not found"}), 404

        user = current_user()

        # Insecure object access:
        # any authenticated user can download if upload id is known
        log_event(user["id"], "download_upload", f"upload_id={upload_id}", user["tenant_id"])
        return send_from_directory(
            current_app.config["UPLOAD_FOLDER"],
            upload["stored_filename"],
            as_attachment=True,
            download_name=upload["original_filename"],
        )

    @app.get("/admin/audit-export")
    @require_role("it_admin", "compliance_admin")
    def audit_export():
        user = current_user()

        # Insecure: supports cross-tenant export via query param
        export_scope = request.args.get("scope", "tenant")
        if export_scope == "all":
            events = fetch_all_audit_events()
        else:
            tenant_id = request.args.get("tenant_id", user["tenant_id"])
            events = fetch_audit_events_for_tenant(tenant_id)

        return jsonify(events)

    @app.post("/admin/import-url")
    @require_role("it_admin", "compliance_admin")
    def import_url():
        data = request.get_json(silent=True) or {}
        url = data.get("url", "")
        lowered = url.lower()

        # Superficial fix only blocks localhost string and one loopback literal
        if "localhost" in lowered or "127.0.0.1" in lowered:
            return jsonify({"error": "internal urls forbidden"}), 400

        if not url.startswith("http://") and not url.startswith("https://"):
            return jsonify({"error": "unsupported scheme"}), 400

        try:
            resp = requests.get(
                url,
                timeout=current_app.config["DEFAULT_IMPORT_TIMEOUT"],
                allow_redirects=True,
            )
            snippet = resp.text[:200]
        except Exception as exc:
            return jsonify({"error": str(exc)}), 502

        log_event(
            current_user()["id"],
            "import_url",
            f"url={url}",
            current_user()["tenant_id"],
        )
        return jsonify(
            {
                "message": "url imported",
                "status_code": resp.status_code,
                "preview": snippet,
            }
        )
