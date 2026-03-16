# Threat Model Notes

## Assumptions
- Internal users are not fully trusted
- Tenant boundaries should be enforced server-side
- Administrative functions are sensitive
- File uploads are untrusted input
- Audit logs contain sensitive activity records

## Security Themes
- Broken access control
- Cross-tenant access
- Privilege escalation
- SSRF
- File handling abuse
- Insecure workflow transitions
- Audit overexposure
