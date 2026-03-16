from dataclasses import dataclass

@dataclass
class Tenant:
    id: int
    name: str

@dataclass
class User:
    id: int
    username: str
    role: str
    tenant_id: int
    full_name: str
    email: str

@dataclass
class Profile:
    id: int
    user_id: int
    employee_id: str
    title: str
    department: str
    tenant_id: int

@dataclass
class Ticket:
    id: int
    title: str
    description: str
    created_by: int
    tenant_id: int
    status: str

@dataclass
class ApprovalRequest:
    id: int
    requester_id: int
    target_system: str
    requested_role: str
    justification: str
    status: str
    approved_by: int | None
    tenant_id: int

@dataclass
class Upload:
    id: int
    original_filename: str
    stored_filename: str
    uploaded_by: int
    tenant_id: int

@dataclass
class AuditEvent:
    id: int
    actor_user_id: int | None
    action: str
    details: str
    tenant_id: int
    created_at: str
