# Architecture

## Style

Client–server (three-tier) system with a **layered backend**. Two clients share one REST API; the API is the single source of truth for all business rules.

```
Mobile (Expo, residents) ─┐
                          ├─ HTTPS/JSON + JWT ─► FastAPI ─► PostgreSQL 16 + PostGIS
Web (React, officials) ───┘                        ├──────► Object storage (Cloudflare R2, presigned URLs)
                                                   └──────► Notifications (Expo Push, Brevo email, in-app DB alerts)
```

## Components

| Component | Tech | Responsibility |
|---|---|---|
| Mobile | React Native + Expo, TypeScript | Resident reporting, GPS/map pin, offline drafts, push, timeline, rating |
| Web | React + Vite + TypeScript, Tailwind, TanStack Query, Recharts, Leaflet | Admin and personnel workflows, dashboard, heatmap, exports |
| API | FastAPI, Python 3.12, Pydantic, SQLAlchemy 2.0, Alembic | Auth, RBAC, validation, business rules, OpenAPI contract |
| Database | PostgreSQL 16 + PostGIS | Relational data, spatial queries (barangay tagging, heatmap, duplicates) |
| Storage | Cloudflare R2 (Supabase Storage fallback) | Report and resolution photos, private, presigned access only |
| Maps | OpenStreetMap tiles; Leaflet (web), react-native-maps (mobile) | Display only; spatial math happens in PostGIS |

## Backend layers (`api/app/`)

| Layer | Folder | Does | Must not |
|---|---|---|---|
| Routers | `routers/` | Parse HTTP, apply RBAC dependencies, call a service, return a schema | Contain business rules or raw queries |
| Schemas | `schemas/` | Pydantic request/response models; defines the API contract | Import SQLAlchemy models into responses directly |
| Services | `services/` | Business rules: status transitions, priority scoring, assignment, dedup, notifications, retention | Know about HTTP (no `Request`, no status codes) |
| Models | `models/` | SQLAlchemy ORM classes | Contain workflow logic |
| DB | `db/` | Engine, session, transaction helpers | — |
| Core | `core/` | Config, security (JWT, hashing), shared enums | — |

Dependency direction is one way: routers → services → models/db. Services may call other services.

## Clients

- Server state goes through the typed API client in `src/api/` and TanStack Query hooks. Components don't call `fetch` directly.
- Clients display status, category and priority labels from API-served enums; they don't hardcode them.
- Mobile keeps drafts locally (`expo-sqlite`) and syncs with an idempotency key.

## Key flows

1. **Report intake:** mobile uploads photos → API validates → one transaction creates the report, media records and the first `SUBMITTED` history row → PostGIS resolves `barangay_id` → duplicate check → admin alert.
2. **Status change:** router checks role → status service validates the transition (409 if illegal) → inserts history row → notification dispatcher queues push/email/in-app. A failed notification never rolls back the transition.
3. **Dashboard:** aggregation runs in SQL; the browser receives aggregates, never bulk raw coordinates.

## Deployment

API on Render/Railway, Postgres on Supabase/Neon, web on Vercel/Netlify, mobile via EAS Build (Play internal testing + APK). Local development via `docker compose up`.

## Decisions

Record architectural decisions as ADRs in [adr/](adr/).
