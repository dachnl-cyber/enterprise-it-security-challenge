from functools import wraps
from flask import session, jsonify

VALID_ROLES = {"employee", "manager", "it_admin", "compliance_admin"}

def current_user():
    return session.get("user")

def is_authenticated():
    return current_user() is not None

def require_login(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return jsonify({"error": "authentication required"}), 401
        return view_func(*args, **kwargs)
    return wrapper

def require_role(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                return jsonify({"error": "authentication required"}), 401
            if user["role"] not in allowed_roles:
                return jsonify({"error": "forbidden"}), 403
            return view_func(*args, **kwargs)
        return wrapper
    return decorator

def same_tenant(user, tenant_id):
    return user["tenant_id"] == tenant_id

def weak_tenant_gate(user, tenant_id):
    if user["role"] in {"it_admin", "compliance_admin"}:
        return True
    return user["tenant_id"] == tenant_id
