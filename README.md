# Enterprise IT Security Challenge

This repository contains an intentionally vulnerable internal multi-tenant Enterprise IT admin platform designed for advanced security review and remediation.

## Primary Domain
Enterprise IT

## Security Task Types
- Vulnerability Discovery & Analysis
- Vulnerability Remediation
- Security Code Review
- Penetration Testing
- Secure Code Generation

## Scenario
The platform is used across multiple subsidiaries of a parent organization. Each subsidiary is treated as a separate tenant. Users include `employee`, `manager`, `it_admin`, and `compliance_admin`.

The application supports:
- login
- employee profile lookup
- support tickets
- compliance evidence uploads
- privileged-access approval workflows
- audit log export
- admin URL import

The codebase is intentionally vulnerable and includes incomplete or superficial fixes. The task is to identify the full scope of the issues, remediate them properly, preserve intended functionality, and add regression tests.

## Setup
1. Create a Python virtual environment
2. Install dependencies from `requirements.txt`
3. Run the Flask app
4. Use the seeded demo accounts
5. Run the test suite

## Demo accounts
- alice / password123
- mary / password123
- ian / password123
- claire / password123
- bob / password123
