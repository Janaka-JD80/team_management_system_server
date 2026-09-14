# RBAC (Roles & Permissions) Runbook

## 1. Executive Summary & Purpose
This document outlines the architecture for the Dynamic Role-Based Access Control (RBAC) system. The implementation uses a normalized, many-to-many database schema allowing Administrators to grant granular permissions to users without requiring code deployments.

---

## 2. Architecture Overview

The Identity Store relies on 5 relational tables:
1. `users`: The core entity.
2. `roles`: e.g., "TEAM_MEMBER", "MANAGER", "ADMIN".
3. `permissions`: e.g., "CREATE_REPORT", "VIEW_DASHBOARD".
4. `user_roles`: Maps users to roles (Many-to-Many).
5. `role_permissions`: Maps roles to specific permissions (Many-to-Many).

### RBAC Authorization Flow (Exact Flow)

**Step 1: API Request Initiation**
- The user attempts to access a protected endpoint (e.g., `GET /api/v1/analytics`).
- The client browser automatically includes the HTTP-Only `access_token` cookie in the request.

**Step 2: Middleware Token Validation**
- The FastAPI `AuthMiddleware` intercepts the request before it reaches the core logic.
- The Middleware validates the JWT HMAC signature to ensure the token hasn't been tampered with.
- The Middleware extracts the `permissions` list directly from the JWT payload (e.g., `["VIEW_DASHBOARD", "CREATE_REPORT"]`).

**Step 3: Controller Permission Check**
- The request passes to the API Controller, which triggers a `RequirePermission("VIEW_DASHBOARD")` dependency check.
- **If the user has the permission:** The Controller executes the business logic and returns a `200 OK` response with the data.
- **If the user lacks the permission:** The Controller instantly aborts the request and returns a `403 Forbidden` response, preventing unauthorized access.

---

## 3. Operational Workflow & API Usage

### 3.1. Create a New Role (Admin Only)
Creates a new role definition in the system.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/roles/" \
     -H "Content-Type: application/json" \
     -H "Cookie: access_token=..." \
     -d '{
       "role_name": "DIRECTOR",
       "description": "Executive level access"
     }'
```

### 3.2. Assign Role to User (Admin Only)
Maps an existing user to a specific role.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/users/user-uuid/roles" \
     -H "Content-Type: application/json" \
     -H "Cookie: access_token=..." \
     -d '{
       "role_id": "role-uuid"
     }'
```

---

## 4. Security & Maintenance Guardrails

- **JWT Embedding:** To prevent executing a massive 5-table JOIN query on every single API request, a user's `permissions` array is serialized directly into their JWT Payload during Login.
- **Privilege Escalation Prevention:** The `roles` and `permissions` endpoints are strictly protected by `RequirePermission("MANAGE_RBAC")`. Only Admins possess this token.

### Error Remediation Codes
| Status Code | Message | Cause & Remediation |
|-------------|---------|---------------------|
| `400` | Role already exists | Attempted to create a duplicate role name. |
| `403` | Forbidden | User lacks the required permission in their JWT payload. |
| `404` | Role not found | The provided `role_id` does not exist during assignment. |
