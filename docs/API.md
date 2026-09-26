# API

The FastAPI OpenAPI spec (`/docs` and `/openapi.json` on a running server, exported to [api/](api/)) is the authoritative contract. This file defines the conventions every endpoint follows.

## Basics

- Base path: `/api/v1`. JSON only. HTTPS only.
- Auth: `Authorization: Bearer <access_token>`.
- Resource names: plural nouns, `kebab-case` paths, `snake_case` JSON fields.
- Timestamps: ISO 8601 in UTC (`2026-10-01T08:30:00Z`).
- Role-scoped routes are grouped by prefix: `/admin/*`, `/personnel/*`; shared resident routes are unprefixed.

## Endpoint groups

| Group | Examples |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/verify-email`, `POST /auth/resend-verification`, `POST /auth/refresh`, `POST /auth/logout` |
| Me | `GET /me`, `PATCH /me`, `POST /me/consents`, `POST /me/device-tokens` |
| Reports (resident) | `POST /reports`, `GET /reports`, `GET /reports/{id}`, `POST /reports/{id}/reopen`, `POST /reports/{id}/rating` |
| Media | `POST /media/upload-url`, `GET /media/{id}/url` |
| Admin | `POST /admin/users` (create personnel/admin accounts), `GET /admin/reports`, `POST /admin/reports/{id}/validate`, `.../reject`, `.../category`, `.../priority`, `.../assign` |
| Personnel | `GET /personnel/queue`, `POST /personnel/reports/{id}/status`, `POST /personnel/reports/{id}/resolution` |
| Analytics | `GET /admin/analytics/summary`, `.../heatmap`, `.../barangays`, `GET /admin/exports/{csv|pdf}` |
| Reference | `GET /enums` (statuses, categories, priority bands, rejection reasons), `GET /barangays` (public; registration form) |

## Tokens

`POST /auth/login` returns `access_token` (15 min) and `refresh_token` (7 d, opaque). `POST /auth/refresh` with `{ "refresh_token" }` returns a new pair and invalidates the one presented; replaying a used token revokes that login's whole token family. `POST /auth/logout` with `{ "refresh_token" }` revokes it (204, idempotent). Role failures return 403 with code `FORBIDDEN`.

## Errors

All errors use one shape:

```json
{ "error": { "code": "INVALID_TRANSITION", "message": "Cannot move from CLOSED to IN_PROGRESS.", "details": {} } }
```

| Status | When |
|---|---|
| 400 | Malformed request |
| 401 | Missing or expired token |
| 403 | Authenticated but not allowed (role or ownership) |
| 404 | Not found, **or** exists but caller may not know it exists |
| 409 | Illegal status transition, duplicate account, idempotency conflict |
| 422 | Validation failure; `details` lists field-level errors |
| 429 | Rate limited |

## Lists

- Pagination: `?page=1&page_size=20` (max 100). Response: `{ "items": [...], "total": 123, "page": 1, "page_size": 20 }`.
- Filters as query params: `status`, `category`, `barangay_id`, `priority`, `date_from`, `date_to`.
- Sorting: `?sort=-created_at` (prefix `-` for descending).

## Idempotency

`POST /reports` accepts an `Idempotency-Key` header (client-generated UUID) so offline drafts can't create duplicates on retry.

## Media

Clients request a presigned upload URL, upload directly to storage, then submit the object key with the report. Reads return short-lived presigned URLs (15 minutes). Never embed permanent media URLs.

## External services

| Service | Used for | Called from |
|---|---|---|
| Expo Push (FCM) | Resident push notifications | API notification dispatcher |
| Brevo | Email (assignment, resolution, verification) | API notification dispatcher |
| Cloudflare R2 | Photo storage | API (presign) and clients (direct upload via presigned URL) |
| OpenStreetMap tiles | Map display | Clients only |

Clients never call Expo Push or Brevo directly, and API keys never ship in client code.

## Versioning

Breaking changes go into a new version prefix (`/api/v2`). Additive changes (new optional fields, new endpoints) stay in `v1`. Note every contract change in the PR description so both client developers see it.
