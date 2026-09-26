# Database

PostgreSQL 16 + PostGIS, accessed through SQLAlchemy 2.0, migrated with Alembic. The ERD lives in [design/erd/](design/erd/).

## Conventions

- Tables: plural `snake_case` (`reports`, `report_status_history`). Columns: `snake_case`.
- Primary keys: `id` (UUID or BIGINT identity; decide in an ADR before the first migration).
- Foreign keys: `<singular>_id` (`report_id`, `barangay_id`), always indexed.
- Every table has `created_at` and `updated_at` as `TIMESTAMPTZ` stored in UTC. Display in Asia/Manila on the clients.
- Enums (status, role, category, priority band, location source) are defined once in `api/app/core` and stored as Postgres enums or lookup tables.
- Geometry: `GEOMETRY(Point, 4326)` for report locations, `GEOMETRY(MultiPolygon, 4326)` for barangays. GiST index on every geometry column.

## Core tables

| Table | Purpose | Notes |
|---|---|---|
| `users` | Residents, personnel, admins | Only name, mobile, email, barangay, password hash, role, office, timestamps |
| `consents` | Privacy consent records | `user_id, policy_version, timestamp, ip` |
| `offices` | Responding offices | Mapped to default categories |
| `barangays` | Boundary polygons | Loaded from PhilGIS/PSA or digitized |
| `categories` | Seeded concern categories | Includes category weight for scoring |
| `reports` | The concern | Reference number, resident/admin category, description, location, `location_source`, `accuracy_m`, `barangay_id`, `barangay_unresolved`, computed and final priority, `priority_breakdown` (JSONB), current status, assignee |
| `report_media` | Report and resolution photos | Object keys only, never URLs |
| `report_status_history` | Lifecycle audit trail | **Insert-only** |
| `assignments` | Assignment and reassignment history | Office, assignee, reason |
| `resolutions` | Action taken and evidence | Narrative, completion date, resources |
| `ratings` | Resident feedback | One per report; editable 7 days |
| `notifications` | Push/email/in-app log | Delivery status |
| `audit_logs` | Sensitive reads and admin actions | Actor, action, target, timestamp |

## Rules

- `report_status_history` and `audit_logs` are append-only: no UPDATE or DELETE path in the application.
- Report creation, media records and the first history row are written in **one transaction**.
- Never hard-delete reports. Rejected reports stay visible to the resident.
- Anonymization (US-28) nulls personal fields and keeps category, barangay, timestamps and history.
- Aggregations for the dashboard and heatmap run in SQL (`GROUP BY`, `ST_SnapToGrid`), not in application code.

## Required indexes

`reports(status)`, `reports(barangay_id)`, `reports(created_at)`, `reports(assignee_id)`, GiST on `reports.location` and `barangays.geom`.

## Migrations

- One Alembic migration per logical change; descriptive message (`add_ratings_table`).
- Autogenerate, then review the file by hand before committing.
- Never edit a migration that has been merged; write a new one.
- Every migration must run cleanly on a fresh database (checked in CI).

## Seed data

Use synthetic data only (`api/scripts/`) until ethics clearance and LGU permission are granted. Never load real resident data into development databases.
