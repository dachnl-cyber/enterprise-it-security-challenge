import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from .db import get_db

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "csv", "html"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file_storage, uploaded_by, tenant_id):
    if not file_storage or not file_storage.filename:
        raise ValueError("missing file")

    # Superficial fix: extension-only validation
    if not allowed_file(file_storage.filename):
        raise ValueError("file type not allowed")

    # Insecure: preserves user-provided name in storage path generation logic
    unsafe_name = file_storage.filename
    cleaned_name = secure_filename(unsafe_name)

    if not cleaned_name:
        raise ValueError("invalid filename")

    # Insecure: predictable-ish composition, original name still discoverable
    stored_filename = f"{uuid.uuid4().hex}_{cleaned_name}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, stored_filename)
    file_storage.save(full_path)

    db = get_db()
    db.execute(
        """
        INSERT INTO uploads (original_filename, stored_filename, uploaded_by, tenant_id)
        VALUES (?, ?, ?, ?)
        """,
        (unsafe_name, stored_filename, uploaded_by, tenant_id),
    )
    db.commit()
    return stored_filename

def list_uploads_for_tenant(tenant_id):
    db = get_db()
    rows = db.execute(
        """
        SELECT id, original_filename, stored_filename, uploaded_by, tenant_id
        FROM uploads
        WHERE tenant_id = ?
        ORDER BY id DESC
        """,
        (tenant_id,),
    ).fetchall()
    return [dict(row) for row in rows]

def get_upload_by_id(upload_id):
    db = get_db()
    row = db.execute(
        """
        SELECT id, original_filename, stored_filename, uploaded_by, tenant_id
        FROM uploads
        WHERE id = ?
        """,
        (upload_id,),
    ).fetchone()
    return dict(row) if row else None
