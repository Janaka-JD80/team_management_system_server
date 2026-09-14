# Report Service Runbook

## 1. Executive Summary & Purpose
This document outlines the workflow and architecture for submitting, reviewing, and managing Weekly Reports within the **Team Management System**. The system implements an **Immutable Audit Trail**, ensuring that any edits or manager corrections spawn a new `report_version` rather than overwriting historical data.

---

## 2. Architecture Overview

The Report Service utilizes two primary database tables to manage state:
1. `reports`: The overarching entity that tracks the final status and ownership of the report.
2. `report_versions`: The granular entity that stores the actual text (tasks, blockers, time spent) and increments a `version_number` every time the report is edited.

### Report Review Workflow (Exact Flow)

**Step 1: Draft & Submit**
- The Team Member inputs their weekly data (tasks, blockers, hours) on the frontend.
- The client sends a `POST /api/v1/reports` request to the backend.
- The backend creates the main `reports` row with the status set to `SUBMITTED`.
- The backend creates the first `report_versions` row (version=1) containing the actual data.

**Step 2: Manager Review**
- The Manager reviews the submitted data on the Team Dashboard.
- The Manager clicks "Needs Correction" and provides a comment.
- The client sends a `PUT /api/v1/reports/{id}/status` request to the backend.
- The backend updates the main `reports` row status to `NEEDS_CORRECTION`.

**Step 3: Team Member Edits (Immutable Audit Trail)**
- The Team Member sees the Manager's comment, edits their data, and clicks "Resubmit".
- The client sends a `PUT /api/v1/reports/{id}` request to the backend.
- The backend updates the main `reports` row status back to `SUBMITTED`.
- The backend **does not** overwrite version 1. Instead, it creates a brand new `report_versions` row (version=2) with the updated data.

---

## 3. Operational Workflow & API Usage

### 3.1. Submit a New Report
Allows a Team Member to submit their weekly progress.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/reports/" \
     -H "Content-Type: application/json" \
     -H "Cookie: access_token=..." \
     -d '{
       "project_id": "proj-uuid",
       "week_start_date": "2026-09-07",
       "tasks_completed": [{"task_name": "API Design"}],
       "blockers": ["Database latency"],
       "hours_worked": {"development": 20}
     }'
```

**Expected Response (200 OK):**
```json
{
  "status": "success",
  "message": "Report submitted successfully.",
  "data": {
    "report_id": "rep-uuid",
    "status": "SUBMITTED",
    "current_version_num": 1
  }
}
```

### 3.2. Manager Updates Report Status
Allows a Manager to approve or reject a report.

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/reports/rep-uuid/status" \
     -H "Content-Type: application/json" \
     -H "Cookie: access_token=..." \
     -d '{
       "status_id": "needs_correction_uuid",
       "manager_comment": "Please add more detail to your blockers."
     }'
```

---

## 4. Security & Maintenance Guardrails

- **Immutable History:** A `PUT` request to update report content MUST NOT update the existing `report_version` row. A new row must be inserted.
- **RBAC Limitations:** 
  - A Team Member can only update a report if the status is `DRAFT` or `NEEDS_CORRECTION`.
  - A Team Member can only view reports where `user_id` matches their own id.
  - Only a Manager can transition a report to `APPROVED`.

### Error Remediation Codes
| Status Code | Message | Cause & Remediation |
|-------------|---------|---------------------|
| `400` | Invalid State Transition | User attempted to edit an `APPROVED` report. Reject action. |
| `403` | Forbidden | Team Member attempted to view another user's report. |
| `404` | Report Not Found | The `report_id` does not exist in the database. |
