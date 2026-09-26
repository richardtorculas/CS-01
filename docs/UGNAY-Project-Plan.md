# UGNAY — Agile Project Plan
**A Community Issue Reporting and Government Response System**
University of Perpetual Help System Laguna – JONELTA · College of Computer Studies · BS Computer Science

---

## Context

This plan exists because UGNAY is a two-client system (resident mobile app + official web app over one shared API) that a 5-person undergraduate team must build, pilot city-wide, and evaluate against a measured baseline — all inside a single academic year. The binding constraint is not the code; it is that **Objective 1 (baseline measurement) and Objective 6 (post-deployment comparison) are both empirical research activities that depend on an external stakeholder (the LGU) whose approval timeline the team does not control.** A plan that sequences only the software will fail the thesis even if the software works.

The plan therefore runs two tracks in parallel from Week 1: a **build track** (backend first, then mobile and web in parallel) and a **research track** (permissions → ethics clearance → baseline field study → post-pilot evaluation). The research track has a hard gate: baseline data must be locked before deployment, because after deployment the "before" state is unrecoverable.

### Stated assumptions (placeholders you left open)

| Placeholder | Assumption used |
|---|---|
| Start date | Monday, **21 September 2026** |
| Final defense | Week of **26–30 April 2027** |
| Duration | **32 calendar weeks**, of which ~3 are semester break (Weeks 13–15) → ~29 working weeks |
| Sprint length | **2 weeks** |
| Weekly hours/member | **10–15 hrs** → ~120 person-hrs/sprint, ~30% to thesis writing → **~26–30 story points/sprint** target velocity |
| Mobile stack | **React Native + Expo** (your choice) |
| Backend stack | **FastAPI (Python) + SQLAlchemy 2.0 + PostgreSQL 16/PostGIS** (derived from your "PostgreSQL, SQLAlchemy ORM" answer — note this **supersedes the MySQL in your manuscript**; see Open Questions #1) |
| Pilot city | Unnamed — plan assumes a Laguna-area city with **~20–30 barangays** and 4–6 responding offices |
| Pilot operating period | **4 weeks** of live use (Weeks 24–27) |
| Mobile OS target | **Android first**, iOS as Future Work (see Open Questions #7) |

---

## 1. Overview

### 1.1 Project summary

In Philippine city governments, resident concerns — damaged roads, clogged drainage, uncollected garbage, broken streetlights — enter through disconnected channels: walk-ins at the city hall, phone calls, and private messages to individual officials. The report stops at submission. There is no unified workflow that categorizes, prioritizes, assigns, and tracks a concern through to a documented resolution. Residents cannot see progress, reports become untraceable when the receiving staff member is unavailable, and city administrators have no consolidated city-wide picture of what is being reported or resolved.

**UGNAY** is a city-level, low-cost system that connects the full life of a community concern:

> Citizen → Report + Evidence + Location → Validation → Categorization → Priority → Assignment → Action → Resolution Evidence → Status Transparency → Citizen Feedback → Analytics → Administrative Decision

It ships as **two clients over one shared REST API**:

- **Mobile app (residents)** — account creation, privacy notice and consent, concern submission with category, description, photo, and device GPS with manual map-pin fallback; status tracking; push notifications; viewing documented resolutions; rating the resolution.
- **Web app (officials)** — *Personnel*: assigned-concern queue, status updates, resolution documentation with photo evidence. *Administrators*: validation, categorization, rule-based priority scoring, assignment, city-wide monitoring, analytics dashboard, GIS heatmaps, and administrative reports.

**Target users:** residents of the pilot city; city/barangay personnel in responding offices (engineering, sanitation, general services); city administrators.

**Setting:** one pilot city, **city-wide** — all barangays and all participating offices. Every report is geotagged and auto-assigned to a barangay so that both operations and analytics can be viewed city-wide or filtered down to a single barangay.

**Gap addressed:** DILG Online Sumbungan handles corruption complaints; eGovPH eCMS is a national complaint intake; Marikina's e-Concern emphasizes submission and responsiveness. None documents an *integrated* workflow spanning prioritization, assignment, documented resolution, resident feedback, and analytics. UGNAY targets exactly that integration at an affordable city scale.

### 1.2 Goals mapped to the six specific objectives

| # | Specific Objective | Project goal | Primary evidence at defense |
|---|---|---|---|
| **O1** | Document the manual process and establish baselines | Produce a validated as-is process map and a locked baseline dataset for 9 metrics | Baseline Report (signed by LGU focal person) + process flowchart in Ch. 3 |
| **O2** | Reporting module with accounts and privacy notice | Residents submit a complete, geotagged, photo-evidenced report in under 3 minutes with recorded consent | Working mobile app + consent audit log |
| **O3** | Role-based access + administrative module | Admins validate, categorize, score priority (explainably), and assign — with every action attributable | Working web admin module + RBAC test matrix |
| **O4** | Lifecycle tracking, notifications, resolution docs, rating | Every report has a visible, timestamped, append-only status history ending in documented resolution and a resident rating | Status-history audit trail + resolution evidence gallery |
| **O5** | Analytics dashboard + administrative reports | Administrators see counts, categories, locations, status, resolution trends, and GIS heatmaps, exportable as reports | Live dashboard + exported PDF/CSV report |
| **O6** | Evaluate against baseline + verify privacy compliance | Statistically compare post-pilot metrics to baseline; pass an RA 10173 compliance checklist | Ch. 4 results tables + completed privacy checklist |

### 1.3 Scope summary

**In scope**
- Resident mobile app (Android-first, React Native/Expo)
- Officials' web app (personnel + administrator roles)
- Shared REST API, PostgreSQL/PostGIS database, role-based authentication
- Controlled image/document storage with access control
- Device GPS capture with manual map-pin fallback
- Notifications: push (mobile), email, in-system alerts (web)
- Rule-based, explainable priority scoring
- Analytics dashboard with GIS heatmaps and exportable administrative reports
- City-wide coverage of one pilot city across all its barangays
- Baseline measurement, pilot deployment, and post-deployment evaluation

**Out of scope** (per your brief — do not let these drift back in)
- More than one pilot city; results may not generalize
- Corruption or administrative complaints against officials
- Replacement of emergency hotlines (911, BFP, PNP)
- Integration with eGovPH eCMS or any existing city information system
- Machine-learning prioritization (rule-based only)
- Guaranteeing resolution — the system tracks and documents it, it does not perform it
- Offline operation beyond draft saving; a device and internet connection are required
- iOS release (Future Work)

### 1.4 How city-wide coverage across barangays is handled

This is the design decision that makes "city-wide" tractable rather than just a larger number of rows.

1. **Barangay boundary layer.** Load the pilot city's barangay boundary polygons (PhilGIS / PSA shapefiles, or hand-digitized from the city planning office if unavailable) into a PostGIS `barangays` table as `GEOMETRY(MultiPolygon, 4326)`.
2. **Automatic tagging at intake.** When a report arrives with a lat/lng, the API runs a single `ST_Contains` point-in-polygon query and stamps `report.barangay_id`. No resident ever picks a barangay from a dropdown — this removes the single largest source of mis-tagged location data.
3. **Fallback chain.** If the point falls outside all polygons (GPS drift near a boundary, or a manual pin dropped imprecisely), the report is flagged `barangay_unresolved` and lands in the admin validation queue for manual assignment. This is a designed path, not an error.
4. **Filtering.** Every list endpoint and every dashboard widget accepts an optional `barangay_id` filter. Default view is city-wide; one dropdown scopes the entire dashboard to a barangay.
5. **Per-barangay analytics.** The dashboard exposes a barangay comparison table (reports per 1,000 residents, median resolution time, open backlog, average rating) and the heatmap aggregates by grid cell so that dense barangays do not visually swamp sparse ones.
6. **Assignment routing.** Assignment is to an **office** (and a person within it), not to a barangay. Barangay is a *dimension for analysis and filtering*, not a routing key — this keeps the workflow city-wide while the reporting stays geographically granular.

### 1.5 Proposed architecture

```
┌──────────────────────┐        ┌───────────────────────────┐
│  MOBILE (Residents)  │        │  WEB (Personnel + Admins) │
│  React Native / Expo │        │  React + Vite + TypeScript│
│  • submit + photo    │        │  • validate/categorize    │
│  • GPS / manual pin  │        │  • priority review        │
│  • status timeline   │        │  • assign / update status │
│  • push notifications│        │  • resolution upload      │
│  • rate resolution   │        │  • dashboard + heatmap    │
└──────────┬───────────┘        └─────────────┬─────────────┘
           │        HTTPS / JSON (JWT bearer) │
           └────────────────┬─────────────────┘
                            ▼
              ┌─────────────────────────────┐
              │   SHARED REST API           │
              │   FastAPI (Python 3.12)     │
              │   • RBAC middleware         │
              │   • Pydantic validation     │
              │   • priority scoring service│
              │   • notification dispatcher │
              │   • OpenAPI contract (auto) │
              └──┬────────┬─────────┬───────┘
                 │        │         │
    ┌────────────▼──┐ ┌───▼──────┐ ┌▼──────────────────┐
    │ PostgreSQL 16 │ │ Object   │ │ Notification svc  │
    │ + PostGIS     │ │ Storage  │ │ • Expo Push (FCM) │
    │ SQLAlchemy 2.0│ │ (R2 /    │ │ • Email (Brevo)   │
    │ Alembic       │ │ Supabase)│ │ • In-app (DB)     │
    │ barangay polys│ │ presigned│ └───────────────────┘
    └───────────────┘ └──────────┘
                 │
    ┌────────────▼────────────────────────┐
    │ Map / GIS: OpenStreetMap tiles      │
    │ Leaflet + leaflet.heat (web)        │
    │ react-native-maps (mobile pin)      │
    │ PostGIS does the spatial math       │
    └─────────────────────────────────────┘
```

**Technology justification**

| Layer | Choice | Why (for *this* team, *this* budget) |
|---|---|---|
| Backend | **FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic** | Auto-generates the OpenAPI contract, which is the artifact that lets mobile and web be built in parallel by two different people without a meeting. Pydantic gives request validation for free — directly serves the "report completeness" metric. Alembic makes schema evolution across 10 sprints safe. Python is the most likely shared language in a CS cohort. |
| Database | **PostgreSQL 16 + PostGIS** | PostGIS gives you `ST_Contains` (barangay auto-tagging) and `ST_SnapToGrid`/`ST_ClusterDBSCAN` (heatmap aggregation, duplicate detection) as one-line SQL. Doing this in MySQL means writing point-in-polygon logic yourself — weeks of avoidable work. JSONB stores the explainable priority breakdown natively. |
| Mobile | **React Native + Expo (managed)** | One codebase, and `expo-location`, `expo-image-picker`, `expo-notifications`, `expo-sqlite` (offline drafts) cover every device capability you need without touching native code. **Cross-platform beats native here** — a 5-person team cannot staff separate Kotlin and Swift tracks, and Expo's OTA updates + EAS Build let you push pilot fixes without a new APK install, which matters enormously during a 4-week live pilot. |
| Web | **React + Vite + TypeScript + Tailwind + TanStack Query** | Same language family as the mobile client, so the mobile and web devs can review each other's code. TanStack Query removes hand-written loading/caching state. Tailwind gets a professional-looking admin UI without a designer. |
| Charts | **Recharts** | Declarative React charts; sufficient for counts, trends, and category breakdowns. Free. |
| Maps/GIS | **Leaflet + react-leaflet + leaflet.heat over OpenStreetMap tiles** | **No API key, no credit card, no billing surprise.** This directly kills the "map API cost/quota" risk. Google Maps Platform requires a card on file; OSM does not. On mobile, `react-native-maps` uses the Android Maps SDK, which is free for mobile map display. |
| Auth | **JWT access (15 min) + refresh (7 d), argon2 hashing, RBAC dependency injection** | Stateless, works identically for both clients, no session store to host. |
| Storage | **Cloudflare R2** (free tier, zero egress fees) with presigned URLs; Supabase Storage as alternate | Photos must never be publicly enumerable — presigned, short-lived URLs satisfy the RA 10173 proportionality requirement. Zero egress is the difference between free and a surprise bill. |
| Notifications | **Expo Push (free, wraps FCM)** + **Brevo** email (300/day free) + DB-backed in-app alerts | All three channels the brief requires, all at ₱0. |
| Hosting | **Render / Railway** free-to-hobby tier for API; **Supabase** or **Neon** free Postgres (PostGIS-enabled); static web app on **Vercel/Netlify** free | Total expected cost ₱0–₱600/month. Budget a **₱1,500 contingency** for a DigitalOcean $6 droplet if free tiers throttle during the pilot. |
| CI/Repo | **GitHub (free, private) + GitHub Actions** | GitHub Student Developer Pack covers everything. CI runs lint + tests on every PR. |
| Project mgmt | **GitHub Projects** (free Kanban, linked to issues) | Sprint board and backlog live next to the code; no Jira license. |

**Cross-platform vs. native — the recommendation:** use **cross-platform (Expo)**. The thesis contribution is the *integrated workflow*, not native performance. Native Android would buy you marginally better camera/GPS performance and cost you the iOS path, the OTA update capability, and roughly 3 sprints of the mobile developer's time. Ship Android-first via Expo, sideloaded APK or Google Play internal testing track; document iOS as Future Work.

### 1.6 Team

Five members: **Follante, Manalo, Ramos, Rivera, Torculas**. Roles and ownership have **not been finalized** and will be assigned by the team. Everyone writes thesis chapters.

**Areas of work that need an owner and a named backup** (so no single point of failure): product backlog and sprint ceremonies · LGU liaison and ethics clearance · backend and database · mobile app · web app · QA and testing · research instruments and statistical analysis · thesis chapters. Every member takes at least one turn as sprint demo presenter.

**Cadence:** sprint planning Monday of odd weeks (1.5 h), async daily standup in a group chat (3 lines: done / doing / blocked), sprint review + retrospective Friday of even weeks (1.5 h), adviser consultation at least once per sprint.

---

## 2. User Stories

**Estimation baseline:** 1 pt ≈ 2–3 focused hours for this team. 1/2/3 = small, 5 = a day's work, 8 = spans several sessions, 13 = should probably be split but is left whole where it is genuinely one cohesive feature.

**Totals:** Must-Have **164 pts** · Should-Have **68 pts** · Nice-to-Have **47 pts**. At ~28 pts/sprint across 8 development sprints (224 pts capacity), Must-Have + most of Should-Have fits with room for defect work.

### 2.1 MUST-HAVE

---
**US-01** · `[Backend/Both]` · **5 pts** · Obj 2
> As a **resident**, I want to create an account with my name, mobile number, email, and barangay so that my reports are attributable to me and I can track them.

- AC1: Registration rejects duplicate email/mobile with a specific error; password minimum 8 chars, argon2-hashed, never returned in any response.
- AC2: Email (or SMS OTP) verification is required before the first report can be submitted.
- AC3: A resident can update their profile but cannot change their role.
- AC4: The `users` table stores only: name, mobile, email, barangay, hashed password, timestamps — no address, no birthdate, no ID number (proportionality, RA 10173).

---
**US-02** · `[Backend/Both]` · **8 pts** · Obj 3
> As an **administrator**, I want role-based authentication with distinct resident, personnel, and administrator roles so that each user can only access functions appropriate to their role.

- AC1: JWT access token (15 min) + refresh token (7 d); refresh rotation invalidates the used token.
- AC2: A resident's token returns `403` on every `/admin/*` and `/personnel/*` endpoint; a personnel token returns `403` on assignment and scoring endpoints.
- AC3: Personnel and administrator accounts can be created **only** by an administrator — there is no public officials' signup.
- AC4: An RBAC test matrix (3 roles × all protected endpoints) passes in CI.

---
**US-03** · `[Mobile]` · **3 pts** · Obj 2, 6
> As a **resident**, I want to see a plain-language privacy notice and give explicit consent before my first submission so that I know what data is collected and why.

- AC1: The notice states: what is collected (name, contact, photo, GPS), why, who can see it, how long it is kept, and how to request deletion — in English and Filipino.
- AC2: The Submit button is disabled until the consent checkbox is ticked; consent is not pre-ticked.
- AC3: Consent is persisted server-side as `{user_id, policy_version, timestamp, ip}` in a `consents` table.
- AC4: The notice is re-shown and re-consented whenever `policy_version` increments.

---
**US-04** · `[Mobile]` · **5 pts** · Obj 2
> As a **resident**, I want to submit a concern with a category and a description so that the city knows what the problem is.

- AC1: Category is a required single-select from the seeded list (damaged road, clogged drainage, uncollected garbage, broken streetlight, flooding, fallen tree/debris, other).
- AC2: Description is required, 20–1000 characters, with a live character counter.
- AC3: Selecting "other" requires a free-text sub-label.
- AC4: A submitted report appears in the resident's "My Reports" list within 3 s with status `SUBMITTED` and a human-readable reference number (`UGNAY-2026-000123`).

---
**US-05** · `[Mobile]` · **5 pts** · Obj 2
> As a **resident**, I want to attach photo evidence by taking a picture or choosing one from my gallery so that officials can see the actual condition.

- AC1: 1–3 photos per report; at least one is required.
- AC2: Camera and gallery permissions are requested with an in-app rationale before the OS prompt; denial shows a recovery path, not a crash.
- AC3: Images are downscaled client-side to max 1600 px on the long edge and JPEG q80 before upload (keeps uploads viable on mobile data).
- AC4: Upload progress is visible; a failed upload is retryable without re-entering the form.

---
**US-06** · `[Mobile]` · **8 pts** · Obj 2
> As a **resident**, I want the app to capture my GPS location automatically, with the ability to drop a pin manually, so that the report is correctly located even when GPS is weak.

- AC1: On opening the location step, the app requests foreground location and shows the device fix with its accuracy radius in metres.
- AC2: If accuracy is worse than 50 m, or permission is denied, or no fix arrives in 15 s, the app automatically switches to manual pin mode with a visible explanation.
- AC3: The resident can always override the auto-fix by dragging the pin; the report records `location_source` as `GPS` or `MANUAL_PIN` and `accuracy_m`.
- AC4: A nearest-landmark free-text field is offered as a supplementary hint (not a replacement for coordinates).

---
**US-07** · `[Backend]` · **5 pts** · Obj 2, 5
> As an **administrator**, I want every report automatically tagged to a barangay from its coordinates so that city-wide data can be filtered and analyzed per barangay without relying on resident input.

- AC1: Barangay polygons for the pilot city are loaded into PostGIS with SRID 4326.
- AC2: On intake, `ST_Contains` resolves `barangay_id`; the query completes in under 100 ms.
- AC3: A point outside all polygons sets `barangay_unresolved = true` and surfaces in the admin queue with a map and a manual barangay selector.
- AC4: Automated test: 10 known coordinates (including 2 near-boundary and 1 outside the city) resolve to the expected barangay or to unresolved.

---
**US-08** · `[Backend]` · **8 pts** · Obj 2
> As a **resident**, I want my submission reliably received and stored with its evidence so that my report cannot silently disappear.

- AC1: `POST /api/v1/reports` validates every field with Pydantic and returns field-level errors on `422`.
- AC2: Images upload to object storage; only the object key is stored in the DB; retrieval is by presigned URL valid for 15 minutes.
- AC3: Report creation and media attachment occur in one transaction — a failed image upload does not create an orphaned report.
- AC4: Every report receives an immutable reference number and an initial `SUBMITTED` entry in `report_status_history`.

---
**US-09** · `[Web]` · **5 pts** · Obj 3
> As an **administrator**, I want a validation queue of incoming reports so that I can confirm legitimate concerns and reject spam, duplicates, or out-of-scope items.

- AC1: The queue lists new reports with thumbnail, category, barangay, submitted-at, and age, sorted oldest-first by default.
- AC2: Validate → status `VALIDATED`. Reject → requires selecting a reason (spam / not a city concern / insufficient information / emergency — refer to hotline / duplicate) and an optional note.
- AC3: A rejection notifies the resident with the reason; a rejected report remains visible to the resident and is never deleted.
- AC4: Reports flagged as emergency-type display a banner reminding the admin that UGNAY does not replace emergency hotlines.

---
**US-10** · `[Web]` · **3 pts** · Obj 3
> As an **administrator**, I want to confirm or correct the category a resident chose so that analytics reflect the true nature of each concern.

- AC1: The admin can change the category during validation; both `resident_category` and `admin_category` are retained.
- AC2: A category change is written to the audit log with actor and timestamp.
- AC3: Analytics use `admin_category` where present, otherwise `resident_category`.

---
**US-11** · `[Backend/Both]` · **8 pts** · Obj 3
> As an **administrator**, I want the system to compute an explainable rule-based priority score so that urgent concerns rise to the top for a reason I can defend.

- AC1: Score = `(0.30·Urgency + 0.25·Severity + 0.20·AffectedPeople + 0.15·CategoryWeight + 0.10·LocationSensitivity) × 20`, each factor on a 1–5 scale, producing 0–100. Bands: **Critical 80–100 · High 60–79 · Medium 40–59 · Low < 40**.
- AC2: The full breakdown (each factor value, its weight, its contribution, the rule version) is persisted as JSONB and returned by the API.
- AC3: The web UI renders a "Why this score?" panel listing each contributing factor in plain language.
- AC4: The algorithm is deterministic — identical inputs always produce an identical score — verified by unit tests covering all four bands. **No machine learning.**

---
**US-12** · `[Web]` · **5 pts** · Obj 3
> As an **administrator**, I want to review and override the computed priority with a recorded reason so that human judgment remains final.

- AC1: The admin can set a final priority band different from the computed one; a reason is mandatory on override.
- AC2: Both `computed_priority` and `final_priority` are stored; the report detail shows both.
- AC3: The dashboard reports the override rate (a useful Chapter 4 finding about algorithm acceptance).

---
**US-13** · `[Web]` · **5 pts** · Obj 3
> As an **administrator**, I want to assign a validated report to a responding office and a specific personnel member so that ownership is unambiguous.

- AC1: Assignment requires an office and a person within that office; the resulting status is `ASSIGNED`.
- AC2: Assignment triggers an in-app alert + email to the assignee and a push notification to the resident.
- AC3: Reassignment is allowed, requires a reason, and preserves the full assignment history.
- AC4: An unassigned report older than 48 h is visually flagged in the queue.

---
**US-14** · `[Web]` · **5 pts** · Obj 4
> As **personnel**, I want a queue of only the concerns assigned to me, ordered by priority and age, so that I know what to work on next.

- AC1: The queue contains only reports where the logged-in user is the assignee — verified by the RBAC test matrix.
- AC2: Default sort is final priority descending, then age descending; the personnel member can filter by status.
- AC3: Each row shows reference number, category, barangay, priority band, age, and current status.

---
**US-15** · `[Backend/Both]` · **8 pts** · Obj 4
> As an **administrator**, I want every status change recorded in an append-only history so that no report becomes untraceable.

- AC1: Lifecycle: `SUBMITTED → VALIDATED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`, with `REJECTED` reachable from `SUBMITTED` and `REOPENED` reachable from `RESOLVED`.
- AC2: Invalid transitions are rejected by the API with `409` — enforced server-side, not in the UI.
- AC3: `report_status_history` rows are insert-only; there is no UPDATE or DELETE path exposed anywhere in the application.
- AC4: Every row carries actor, role, timestamp, from-status, to-status, and optional note.

---
**US-16** · `[Web]` · **3 pts** · Obj 4
> As **personnel**, I want to update the status of my assigned concern so that residents and administrators can see that work is underway.

- AC1: Only transitions legal from the current status are offered in the UI.
- AC2: Moving to `IN_PROGRESS` requires a short remark.
- AC3: Each update fires a resident push notification and an admin in-app alert.

---
**US-17** · `[Web]` · **8 pts** · Obj 4
> As **personnel**, I want to upload resolution documentation with photo evidence so that the completed action is on record.

- AC1: Marking `RESOLVED` requires an action-taken narrative (min 20 chars) **and** at least one "after" photo — the API enforces both.
- AC2: Resolution photos are stored under the same access controls as report photos.
- AC3: Optional fields: date completed, materials/resources used, personnel involved.
- AC4: A resolved report is visible to the resident with before/after photos side by side.

---
**US-18** · `[Mobile]` · **5 pts** · Obj 4
> As a **resident**, I want to see a timeline of my report's progress so that I do not have to call or visit to follow up.

- AC1: "My Reports" lists all of the resident's reports with current status badges.
- AC2: The detail view shows the full status history as a vertical timeline with dates and the acting office (office name, **not** the individual staff member's personal details).
- AC3: Pull-to-refresh updates the timeline; the list is cached so it renders offline (read-only).

---
**US-19** · `[Mobile]` · **3 pts** · Obj 4
> As a **resident**, I want to view the documented resolution of my concern so that I can confirm what was actually done.

- AC1: When status is `RESOLVED`, the resident sees the action narrative, completion date, and after-photos.
- AC2: Photos load via presigned URLs and are pinch-zoomable.
- AC3: If the resident believes the concern is unresolved, a "Report still unresolved" action moves the report to `REOPENED` with a mandatory reason (max once per report; a second dispute escalates to an admin).

---
**US-20** · `[Backend/Both]` · **8 pts** · Obj 4
> As a **resident**, I want to be notified when my report's status changes so that I do not need to keep checking the app.

- AC1: Push notifications via Expo Push on every status transition; device token registered at login and cleared at logout.
- AC2: Email notification on `ASSIGNED` and `RESOLVED` (the two moments residents care about most) via Brevo.
- AC3: In-system alerts for personnel (new assignment) and administrators (new report, overdue report).
- AC4: All notifications are logged in a `notifications` table with delivery status; a push failure never fails the underlying status transition.

---
**US-21** · `[Mobile]` · **5 pts** · Obj 4
> As a **resident**, I want to rate how my concern was resolved so that the city receives feedback on service quality.

- AC1: A 1–5 star rating with an optional comment becomes available only when status is `RESOLVED`.
- AC2: One rating per report, editable for 7 days, then locked.
- AC3: Submitting a rating moves the report to `CLOSED`; a report auto-closes after 14 days without a rating.
- AC4: Ratings are visible to administrators in aggregate; individual comments are visible with the resident's name masked to initials.

---
**US-22** · `[Web]` · **8 pts** · Obj 5
> As an **administrator**, I want a dashboard of city-wide concern data so that I can make informed administrative decisions.

- AC1: KPI tiles: total reports, open, in progress, resolved, average resolution time, average rating — all respecting the active filters.
- AC2: Charts: reports by category (bar), reports by status (donut), reports over time (line), top 10 barangays by volume (horizontal bar).
- AC3: A barangay comparison table with volume, median resolution time, open backlog, and mean rating, sortable by any column.
- AC4: Dashboard loads in under 3 s with 1,000 seeded reports; aggregation is done in SQL, not in the browser.

---
**US-23** · `[Backend]` · **8 pts** · Obj 6
> As a **resident**, I want my personal information protected so that reporting a concern does not expose me.

- AC1: No endpoint returns resident name, mobile, email, or home coordinates to a personnel or resident caller — only administrators see contact details, and only on reports they administer.
- AC2: Media is served exclusively via short-lived presigned URLs; direct bucket listing is disabled.
- AC3: All traffic is HTTPS; passwords argon2; secrets in environment variables, never committed (CI secret-scanning enabled).
- AC4: An `audit_logs` table records every read of resident contact details with actor, target, and timestamp.

---
**US-24** · `[Research]` · **8 pts** · Obj 1
> As a **researcher**, I want documented baseline measurements of the current manual process so that post-deployment improvements can be proven rather than claimed.

- AC1: An as-is process flowchart is produced from interviews/observation and **validated in writing by the LGU focal person**.
- AC2: All nine baseline metrics (§5.2) are collected with a documented instrument and sample size.
- AC3: The baseline dataset is locked (version-stamped, read-only copy archived) **before** pilot deployment.
- AC4: Data collection follows the approved ethics protocol with signed informed consent from all participants.

---
**US-25** · `[Research]` · **8 pts** · Obj 6
> As a **researcher**, I want post-deployment evaluation instruments for all three user groups so that usability, acceptance, and satisfaction can be measured against theory.

- AC1: SUS (10 items), TAM (PU, PEOU, BI), and D&M IS Success (system quality, information quality, service quality, user satisfaction, net benefits) instruments are assembled, with ECT confirmation items for continuance intent.
- AC2: Instruments are content-validated by the adviser plus two faculty/IT evaluators, and pilot-tested on 5 respondents before full deployment.
- AC3: Cronbach's α is computed per construct; α ≥ 0.70 is the acceptance threshold.
- AC4: Separate forms exist for residents, personnel, and administrators.

---
**US-26** · `[Backend/Both]` · **5 pts** · Obj 6
> As a **user of either client**, I want the system to respond quickly so that it is faster than the manual process it replaces.

- AC1: p95 latency under 2 s for list and detail endpoints, under 5 s for a report submission including one image, measured on a 4G connection.
- AC2: A resident can complete a full submission in under 3 minutes (measured in usability testing).
- AC3: Load test with 50 concurrent users and 1,000 reports shows no 5xx errors (k6 or Locust, free).
- AC4: Indexes exist on `reports(status)`, `reports(barangay_id)`, `reports(created_at)`, `reports(assignee_id)`, and a GiST index on the geometry column.

---
**US-27** · `[Backend/Both]` · **3 pts** · Obj 3, 4
> As an **administrator**, I want the mobile and web clients to always show the same data so that residents and officials never see contradictory information.

- AC1: There is exactly one source of truth — no status or priority logic is duplicated in either client.
- AC2: An E2E test submits on mobile, processes on web, and asserts the mobile timeline matches within one refresh.
- AC3: Status labels, category names, and priority bands come from shared API-served enums, not hardcoded client strings.

---
**US-28** · `[Backend]` · **5 pts** · Obj 6
> As a **data subject**, I want a defined retention and deletion policy so that my data is not kept indefinitely.

- AC1: A written retention schedule: report + media retained 2 years after closure, then media purged and records anonymized; account data deleted 30 days after a deletion request.
- AC2: A resident can request account deletion in-app; the request is logged and actioned within 30 days.
- AC3: An admin-run anonymization routine strips `user_id`, name, and contact from expired records while preserving category, barangay, timestamps, and status history for analytics.
- AC4: The research dataset exported for statistical analysis contains **no** direct identifiers.

---

### 2.2 SHOULD-HAVE

---
**US-29** · `[Web]` · **13 pts** · Obj 5
> As an **administrator**, I want a GIS heatmap of reported concerns so that I can see which areas of the city generate the most concerns.

- AC1: Leaflet map over OSM tiles centred on the pilot city, with a `leaflet.heat` density layer.
- AC2: Filterable by category, status, priority, and date range; barangay boundaries drawn as an optional overlay.
- AC3: Density is computed server-side via `ST_SnapToGrid` aggregation (~100 m cells) — raw coordinates are **never** sent to the browser in bulk (privacy + performance).
- AC4: Renders 1,000 points in under 3 s; the map is exportable as a PNG for the manuscript.

---
**US-30** · `[Web]` · **5 pts** · Obj 5
> As an **administrator**, I want to filter the entire dashboard by barangay, date range, category, and status so that I can drill from city-wide down to one area.

- AC1: Filters apply simultaneously to every tile, chart, table, and the heatmap.
- AC2: Filter state is encoded in the URL so a specific view can be shared or bookmarked.
- AC3: An active-filter summary with a one-click Clear All is always visible.

---
**US-31** · `[Web]` · **8 pts** · Obj 5
> As an **administrator**, I want to export administrative reports as PDF and CSV so that I can bring city-wide data into meetings.

- AC1: PDF includes city seal placeholder, date range, KPI summary, category and status charts, barangay table, and a generated-on footer.
- AC2: CSV exports the filtered report list with all analysis columns.
- AC3: Exports respect the active filters and **exclude resident personal data** unless the exporter is an administrator and ticks an explicit "include contact details" box (logged in the audit trail).

---
**US-32** · `[Backend/Both]` · **8 pts** · Obj 3
> As an **administrator**, I want potential duplicate reports flagged so that the same pothole reported by ten residents becomes one work item with a higher affected-people count.

- AC1: On intake, flag reports within 100 m, same category, within 7 days (PostGIS `ST_DWithin`).
- AC2: The admin sees suggested duplicates side by side and can link them to a parent report.
- AC3: Linking sets children to `DUPLICATE_OF`, notifies those residents that their concern is being handled under the parent, and **raises the parent's AffectedPeople factor** — closing the loop with US-11.
- AC4: Detection is a suggestion only; nothing is auto-merged.

---
**US-33** · `[Mobile]` · **8 pts** · Obj 2
> As a **resident**, I want to compose a report without a connection and have it submit automatically later so that poor signal does not lose my report.

- AC1: Drafts (text, category, photos, coordinates) persist locally in `expo-sqlite`.
- AC2: A queued draft submits automatically when connectivity returns; the resident sees a clear "Pending upload" badge.
- AC3: Failed submissions retry with exponential backoff up to 5 attempts, then surface a manual retry.
- AC4: Duplicate submission is prevented by a client-generated idempotency key honoured by the API.

---
**US-34** · `[Web]` · **5 pts** · Obj 5
> As an **administrator**, I want resolution-trend and aging reports so that I can identify where response is slowing down.

- AC1: Median and mean resolution time by category and by barangay, trended monthly.
- AC2: An aging bucket table (0–3 d, 4–7 d, 8–14 d, 15+ d) for open reports.
- AC3: Reports exceeding a configurable target per priority band are highlighted.

---
**US-35** · `[Web]` · **3 pts** · Obj 3
> As an **administrator**, I want to assign multiple reports at once so that a batch of similar concerns does not take ten separate actions.

- AC1: Multi-select in the queue with a bulk-assign action, capped at 20 per operation.
- AC2: Each report still gets its own assignment record, history entry, and notification.

---
**US-36** · `[Mobile]` · **3 pts** · Obj 4
> As a **resident**, I want to filter and search my report history so that I can find an older report quickly.

- AC1: Filter by status and category; search by reference number or description keyword.
- AC2: Results paginate at 20 with infinite scroll.

---
**US-37** · `[Backend]` · **5 pts** · Obj 2
> As an **administrator**, I want uploaded images normalized server-side so that storage stays within free-tier limits during the pilot.

- AC1: Server generates a 300 px thumbnail and caps the stored original at 1600 px.
- AC2: EXIF is stripped **except** the coordinates already captured in the report record (removes device serials and unintended metadata — a privacy win).
- AC3: Per-report media is capped at 10 MB total.

---
**US-38** · `[Web]` · **5 pts** · Obj 3
> As an **administrator**, I want to create and manage personnel accounts and offices so that the system reflects the city's actual organizational structure.

- AC1: Admin can create/deactivate personnel accounts and assign each to an office.
- AC2: Deactivation blocks login but preserves all historical assignment records.
- AC3: Offices are CRUD-managed and mapped to default categories (e.g., drainage → City Engineering).

---
**US-39** · `[Mobile]` · **5 pts** · Obj 6
> As a **resident**, I want the app in English or Filipino so that I can report a concern in the language I am comfortable with.

- AC1: A language toggle in settings, defaulting to the device locale.
- AC2: All resident-facing strings, including the privacy notice and validation errors, are translated.
- AC3: The choice persists across sessions.

---

### 2.3 NICE-TO-HAVE *(build only if Sprints 1–8 finish early; otherwise → Future Work)*

| ID | Platform | Story (abbrev.) | Pts |
|---|---|---|---|
| **US-40** | Mobile | As a resident, I want an anonymized map of open concerns near me so that I can see if my issue is already reported. *(Requires: no names, no reporter identity, coordinates fuzzed to ~100 m.)* | 8 |
| **US-41** | Web | As an administrator, I want to tune the priority factor weights in a settings screen so that scoring can adapt to city policy without a code change. | 5 |
| **US-42** | Mobile | As a resident, I want voice-to-text for the description so that I can report without typing. | 5 |
| **US-43** | Backend/Both | As a resident without a smartphone data plan, I want SMS status updates so that I am still informed. *(Cost risk: SMS gateways are not free — budget before committing.)* | 8 |
| **US-44** | Web | As personnel, I want the web app usable on my phone browser so that I can update status while in the field. | 5 |
| **US-45** | Backend/Both | As an administrator, I want the dashboard to update in real time via WebSocket so that I see new reports without refreshing. | 8 |
| **US-46** | Web | As an administrator, I want automatic escalation alerts for reports exceeding their target time so that nothing is forgotten. | 5 |
| **US-47** | Mobile | As a resident with low vision, I want large-text and high-contrast modes so that I can use the app comfortably. | 3 |

---

## 3. Risks & Assumptions

### 3.1 Assumptions

| # | Assumption | If it proves false |
|---|---|---|
| A1 | The pilot city LGU grants written permission to study its process, access records, and deploy the pilot. | Fall back to a **simulated/retrospective baseline** built from staff recall interviews plus a role-played walkthrough; reframe the pilot as a usability + feasibility study. This is the single most consequential assumption. |
| A2 | The LGU will share historical concern records (logbooks, call logs, endorsement slips) for at least 3 prior months. | Use a 4-week prospective parallel-logging baseline instead (see Contingency C1). |
| A3 | At least 30 residents, 8 personnel, and 3 administrators will participate in testing and evaluation. | Reduce to a minimum viable sample (20/5/2), report it as a limitation, and use non-parametric tests throughout. |
| A4 | OpenStreetMap tiles and barangay boundary data for the pilot city are available at acceptable quality and at no cost. | Digitize boundaries manually from a city planning map using QGIS (free) — budget ~12 hours. |
| A5 | Personnel and administrators have desktop/laptop web access with a modern browser during working hours. | Prioritize US-44 (mobile-responsive web) out of Nice-to-Have into Should-Have. |
| A6 | Residents own **Android** smartphones (Android 8+) with a camera, GPS, and intermittent mobile data. | iOS users are excluded in the pilot — stated as a limitation; TestFlight is a Future Work item. |
| A7 | The team can work 10–15 hrs/week each, with reduced capacity during the semester break (Weeks 13–15) and midterm/final exam weeks. | Sprint scope is cut, never the sprint's Definition of Done. |
| A8 | The team is competent in JavaScript/TypeScript and Python but weak in DevOps and GIS. | Sprint 0 includes deliberate spikes on PostGIS and deployment; managed hosting (Render/Supabase) is chosen precisely to minimize DevOps exposure. |
| A9 | Institutional research/ethics clearance can be obtained within 6 weeks of application. | Baseline collection slips; Contingency C2 applies. |
| A10 | Free hosting tiers are sufficient for a 4-week pilot at expected volume (< 1,000 reports, < 5 GB media). | Switch to a ₱350/month DigitalOcean droplet from the contingency budget. |

### 3.2 Risk register

Likelihood / Impact: **L** = Low, **M** = Medium, **H** = High.

| ID | Risk | Category | L | I | Mitigation |
|---|---|---|---|---|---|
| **R1** | LGU approval is delayed or refused, blocking baseline access and pilot deployment | Stakeholder | **H** | **H** | Submit the permission letter in **Week 1**, not after the proposal defense. Approach **three** candidate cities in parallel and proceed with whichever responds first. Have the adviser or Dean co-sign. Escalate through a faculty member with an existing LGU contact. Track weekly; declare a decision point at Week 6. |
| **R2** | Institutional ethics/research clearance is delayed | Ethics | **M** | **H** | Prepare the full packet (protocol, instruments, consent forms, privacy notice, data management plan) during **Sprint 0** and submit by Week 2. Sequence work so no sprint before Week 8 depends on clearance. Build with **synthetic seed data** until clearance arrives. |
| **R3** | City-wide scope proves too large for 29 working weeks | Schedule | **H** | **H** | Scope is controlled by the **MoSCoW gate**: only Must-Haves are committed. Barangay is a *tagging and filtering dimension*, not per-barangay feature work — this is what keeps "city-wide" from multiplying effort. Pilot promotion can be staged (5 barangays in Week 22, city-wide in Week 24) without changing the code. |
| **R4** | Building two clients with 5 people overruns the mobile or web track | Technical/Schedule | **H** | **H** | Backend + OpenAPI contract land in Sprints 1–2 so mobile and web proceed in parallel from Sprint 2. Both clients use TypeScript/React so the members working on each client can cover each other. If one track slips, the web app is prioritized (it carries Objectives 3 and 5) and mobile Should-Haves are cut first. |
| **R5** | APK distribution friction and Android device fragmentation | Technical | **M** | **M** | Ship via **Google Play internal testing track** (one-time $25 developer fee) plus a direct APK with written sideload instructions. Test on a minimum device matrix: Android 8/11/14, one low-RAM device, one without Google Play Services. Use Expo OTA updates so pilot fixes do not require reinstallation. |
| **R6** | Low participation in evaluation (residents or staff) | Stakeholder | **H** | **H** | Recruit through barangay officials, not cold outreach. Run **assisted, on-site sessions** at the barangay hall rather than relying on self-service links. Cap the survey at 12 minutes. Offer certificates of participation. Over-recruit by 40%. Begin recruitment in Week 18, not Week 24. |
| **R7** | GPS inaccuracy produces mis-located or mis-tagged reports | Technical/Data | **M** | **M** | Always show the accuracy radius; auto-fall back to manual pin above 50 m (US-06). Record `location_source` and `accuracy_m` as analysis variables. Boundary-straddling points route to the admin queue rather than being silently mis-assigned. Report GPS accuracy distribution as a Chapter 4 finding. |
| **R8** | Map API cost, quota throttling, or a billing requirement | Technical/Budget | **L** | **M** | **Eliminated by design**: OpenStreetMap + Leaflet requires no key, no quota, and no card. Follow the OSM tile usage policy; if volume ever became an issue, switch to a free MapTiler or Stadia key. Do not introduce Google Maps Platform on the web client. |
| **R9** | Scope creep from LGU stakeholders requesting extra features mid-pilot | Stakeholder/Schedule | **H** | **M** | A written scope agreement signed at kickoff. All new requests go to a visible **"Future Work" backlog column** — acknowledged, logged, not built. One designated point of contact (to be assigned) handles requests; only that person can move an item into a sprint. |
| **R10** | A team member becomes unavailable (illness, OJT, academic load, withdrawal) | Schedule | **M** | **H** | Every area of work has a named backup once roles are assigned (§1.6). No knowledge is held by one person: all decisions land in the repo (ADRs), all credentials in a shared vault, all work in tracked issues. Mandatory PR review by a second member. Plan to ~85% of theoretical capacity so a buffer exists. |
| **R11** | Data privacy breach or accidental exposure of resident personal data | Ethics/Data | **L** | **H** | Presigned short-lived media URLs; no public endpoints returning PII; role-gated contact details with audit logging; secrets never committed (CI secret scanning); HTTPS everywhere; a pre-deployment security review sprint (Sprint 8) with an explicit RA 10173 checklist; a written breach-response procedure naming the LGU contact. |
| **R12** | Low resident adoption during the pilot — too few reports to analyze | Stakeholder | **H** | **H** | Coordinate a launch orientation with barangay officials; posters with QR codes at barangay halls; a 3-minute onboarding video in Filipino. Set a **minimum viable pilot dataset of 60 reports**; if volume is short by Week 25, run structured scenario-based sessions with recruited residents to generate additional valid reports, and report this explicitly as a methodological limitation. |
| **R13** | Cloud hosting costs exceed the student budget | Budget | **L** | **M** | Free tiers throughout (Render/Railway, Supabase/Neon, Cloudflare R2, Vercel, Brevo). Set billing alerts at ₱0 where supported. Hold **₱3,000** contingency (₱1,500 hosting fallback + ₱1,400 Play Store fee). Image downscaling and a 10 MB/report cap keep storage inside free limits. |
| **R14** | Real baseline data from the city is unobtainable, incomplete, or unreliable | Data/Research | **H** | **H** | Triangulate three sources: (a) existing records, (b) structured staff interviews, (c) **4 weeks of prospective parallel logging** using a paper/Google Form instrument the team supplies. Any metric with only one source is reported with an explicit reliability caveat. Start this in Week 3. |
| **R15** | Statistical comparison is confounded — pre- and post-periods differ in season, report mix, or staffing | Research | **M** | **M** | Declare the design explicitly as **quasi-experimental one-group pretest–posttest**; state history, maturation, and novelty effects as threats to validity in Ch. 3 and Ch. 5. Stratify comparisons by category where sample size permits. Use non-parametric tests given expected small, non-normal samples. |

### 3.3 Contingency plans for the top 3 risks

**C1 — R1 / R14: LGU approval or baseline data does not materialize (decision point: Week 6)**

*Trigger:* no signed permission by end of Week 6, or the city confirms it holds no usable historical records.

1. **Weeks 1–6, run in parallel:** submit to three candidate LGUs simultaneously. Log every follow-up. Escalate through the College Dean's office at Week 4 if no acknowledgement.
2. **If a city agrees but has no records:** switch Objective 1 to a **prospective parallel-logging baseline** — the team supplies a simple intake log (paper + Google Form) to the receiving desk and records 4 weeks of real walk-ins/calls: timestamp received, channel, category, whether it was endorsed and when, whether a status was ever communicated back, and whether it can be located afterward. This yields *stronger* baseline data than recall interviews and requires no historical records at all. Runs Weeks 8–11.
3. **If no city agrees by Week 6:** pivot to a **process-reconstruction baseline** — interview 3–5 current or former LGU staff (personal networks, faculty contacts, a barangay rather than the city hall), reconstruct the as-is workflow, and validate it with a role-played time-and-motion walkthrough. Reframe the study as a **design-and-usability evaluation** with simulated operational data and recruited resident participants. Objectives 2–5 are unaffected; Objective 6 is rescoped from "improvement over city baseline" to "usability, acceptance, and simulated-process comparison." Communicate this to the adviser in writing the same week.
4. **Hard fallback:** whatever happens, the software track is never blocked — development runs on synthetic seed data (1,000 generated reports across all barangays, built in Sprint 1) from day one.

**C2 — R3 / R4: Schedule slip from city-wide scope and two clients (checkpoint: end of Sprint 5, Week 12)**

*Trigger:* cumulative Must-Have completion is below 60% at the end of Sprint 5, or two consecutive sprints miss their goal.

1. **Immediately:** cut all Should-Haves except US-29 (heatmap) and US-30 (barangay filters) — these two carry Objective 5 and cannot be dropped. Everything else moves to Future Work in the manuscript.
2. **Reallocate:** two members (typically backend and QA) move onto whichever client track is behind for two sprints; backend work reduces to defect fixes and endpoints the clients are actively blocked on.
3. **Feature degradation ladder** (apply in this order, stopping as soon as the schedule recovers):
   - Email notifications → in-app only (keep push, which residents actually see)
   - PDF export → CSV export only
   - Offline drafts (US-33) → dropped entirely
   - Duplicate detection (US-32) → dropped; `AffectedPeople` becomes an admin-entered factor only
   - Heatmap → a static barangay **choropleth** (a coloured boundary map by report count) instead of a kernel-density layer — far cheaper, still satisfies "GIS visualization"
4. **Staged pilot:** deploy to 5 representative barangays in Week 22 and promote city-wide in Week 24. Nothing in the code changes; only the recruitment footprint does. If the schedule is critical, the pilot is *reported* as 5-barangay with city-wide capability demonstrated — an honest, defensible narrowing.
5. **Protect the non-negotiables:** the demo path (submit → validate → score → assign → resolve → rate → dashboard) and the evaluation instruments are never cut. A thesis with a narrow but complete and evaluated system passes; a broad but unevaluated one does not.

**C3 — R6 / R12: Low adoption and low evaluation participation (checkpoint: Week 25, mid-pilot)**

*Trigger:* fewer than 30 reports by the end of pilot Week 2, or fewer than 15 resident evaluation respondents secured by Week 25.

1. **Week 18 (before the pilot, not during):** secure a written commitment from 4–6 barangay captains to endorse the pilot, and pre-register a resident participant list with contact consent. Recruitment is a Sprint 9 deliverable, not an afterthought.
2. **Mid-pilot escalation:** run **on-site reporting clinics** — the team sets up at a barangay hall for a half-day, helps residents install the app and file a genuine concern, and administers the SUS immediately afterward while the experience is fresh. Three clinics across three barangays typically yields 30–45 respondents in a single week and solves the report-volume and survey-response problems together.
3. **Staff-side backstop:** personnel and administrator samples are small (8 and 3) and fully within LGU control — secure these via the permission agreement so that at minimum, two of three user groups are reliably evaluated.
4. **Analytical fallback:** if `n < 30` residents, shift from parametric to **non-parametric tests** (Mann–Whitney U, Wilcoxon signed-rank, two-proportion z-test) — appropriate for small samples — report exact p-values and effect sizes (Cliff's delta or rank-biserial r) rather than relying on significance alone, and state the reduced statistical power as an explicit limitation in Ch. 5. A well-reported small-n study is defensible; a silently underpowered one is not.
5. **Absolute floor:** 20 residents, 5 personnel, 2 administrators, 60 reports. Below this, report the evaluation as a **formative usability study** rather than a summative comparison, and reframe Ch. 4 accordingly.

---

## 4. Plan (Sprint Breakdown)

### 4.0 Global Definition of Done

Every user story, in every sprint, must satisfy all of the following before it is counted:

1. Code merged to `main` via pull request, reviewed and approved by at least one other member.
2. All acceptance criteria demonstrably met, verified by a team member other than the author against the written criteria.
3. Unit tests written for backend business logic; CI (lint + tests) green.
4. API changes reflected in the OpenAPI spec and the Postman collection.
5. Database changes delivered as an Alembic migration that runs cleanly on a fresh database.
6. No new hardcoded secrets, no new PII in logs, no new publicly readable media path.
7. Works on the target matrix: mobile → Android 8/11/14; web → Chrome + Edge at 1366×768 and above.
8. Demonstrated in the sprint review on the staging environment (not on a laptop).
9. Any design decision worth remembering recorded as a one-page ADR in `/docs/adr/`.
10. The corresponding manuscript subsection is drafted or updated in the same sprint.

### 4.1 Parallel research track (runs across all sprints)

This track is scheduled independently of the build. Its owners (a research lead and an LGU liaison) are to be assigned.

| Weeks | Research activity | Gate |
|---|---|---|
| 1–2 | Draft and send LGU permission letters (3 cities); assemble ethics packet | Letters sent by end W2 |
| 2–4 | Ethics submission; design baseline instruments; interview guide; time-and-motion protocol | Ethics submitted by W3 |
| 4–6 | LGU meetings; as-is process observation and interviews; **R1 decision point at W6** | Written LGU permission secured |
| 6–8 | Ethics clearance received; instrument content validation by 3 evaluators; pilot-test instruments on 5 respondents | **Clearance in hand** |
| 8–11 | **Baseline field data collection** — historical records extraction + 4 weeks prospective parallel logging + staff time-and-motion + resident pre-survey | 9 metrics collected |
| 12 | Baseline analysis, as-is flowchart validated and signed by LGU focal person | **Baseline Report v1.0** |
| 16–17 | Baseline dataset **LOCKED** (archived read-only, version-stamped) | ⛔ **HARD GATE — no deployment before this** |
| 18–19 | Evaluation instrument finalization; participant recruitment begins; barangay captain endorsements | 40+ residents pre-registered |
| 22–23 | LGU staff training; orientation materials; launch coordination | Training complete |
| 24–27 | Pilot operation; observation logs; mid-pilot check at W25 (**C3 trigger**) | 60+ reports minimum |
| 26–27 | Post-deployment surveys (SUS/TAM/D&M) across all three groups; system-log metric extraction | All instruments collected |
| 28–29 | Statistical analysis; baseline vs. system comparison; privacy compliance checklist | Ch. 4 complete |

### 4.2 Sprint 0 — Foundation & Clearance · **Weeks 1–2** (Sep 21 – Oct 4)

**Sprint goal:** Everything needed to start building and to start the research clock is in place, and no downstream sprint is blocked on a decision that could have been made now.

| Area | Tasks |
|---|---|
| **Requirements** | Finalize backlog in GitHub Projects; MoSCoW classification agreed and frozen; write the scope agreement for LGU signature; confirm the 9 baseline metrics and their operational definitions |
| **Stakeholder/Ethics** | Draft + send LGU permission letters to 3 candidate cities; assemble ethics packet (protocol, instruments, consent forms, privacy notice, data management plan); submit to the review committee |
| **Design — Mobile** | Wireframes for 9 screens: onboarding, register, privacy consent, submit (3 steps: details → photo → location), my reports, report detail/timeline, resolution view, rating, settings |
| **Design — Web** | Wireframes for 8 screens: login, admin validation queue, report detail + priority panel, assignment, personnel queue, resolution upload, dashboard, reports/export |
| **Data design** | ERD covering 14 entities: `users`, `roles`, `offices`, `barangays` (PostGIS), `reports`, `report_media`, `report_status_history`, `assignments`, `priority_scores`, `resolutions`, `resolution_media`, `ratings`, `notifications`, `consents`, `audit_logs`; data dictionary |
| **API contract** | Author the OpenAPI 3.1 spec **first** — all endpoints, request/response schemas, error shapes, auth scheme. This is the contract that unblocks parallel client work. Publish a Postman collection with mock responses |
| **Priority algorithm** | Define the scoring rubric: factor scales (1–5 each), weights, category weight table, location sensitivity table, band thresholds; write it up for Ch. 3 |
| **Infrastructure** | GitHub repo (monorepo: `/api`, `/mobile`, `/web`, `/docs`); branch protection on `main`; GitHub Actions CI (ruff + pytest + eslint + tsc); provision staging Postgres with PostGIS; Render/Railway staging service; Cloudflare R2 bucket; shared secrets vault |
| **Spikes** | (a) PostGIS point-in-polygon with real barangay shapefiles — 4 h; (b) Expo push notification round-trip on a physical device — 4 h; (c) Leaflet heatmap with 1,000 synthetic points — 3 h. **Each spike must produce a working proof, not a report.** |
| **Thesis** | Ch. 1 complete draft; Ch. 2 RRL outline with 25+ sources identified; Ch. 3 methodology skeleton |

**Deliverables:** frozen backlog · LGU letters sent · ethics packet submitted · mobile + web wireframes · ERD + data dictionary · OpenAPI spec v1 · priority rubric · running CI on a staging environment · 3 completed spikes · Ch. 1 draft.

**Definition of Done (Sprint 0):** a new team member can clone the repo, run `docker compose up`, and hit a live `/health` endpoint against staging Postgres; both wireframe sets have been walked through by the whole team; the OpenAPI spec has been signed off by both client developers as sufficient to build against.

---

### 4.3 Sprint 1 — Backend Foundation & Identity · **Weeks 3–4** (Oct 5 – Oct 18)

**Sprint goal:** Authentication, roles, and the complete data model are live on staging, with synthetic city-wide data seeded — so both clients can start against real endpoints next sprint.

**Stories:** US-01 (5), US-02 (8), US-07 (5), US-28 (5) · **23 pts**

| Track | Tasks |
|---|---|
| **Backend** | FastAPI project scaffold; SQLAlchemy 2.0 models for all 14 entities; Alembic initial migration; argon2 password hashing; JWT access + refresh with rotation; RBAC dependency (`require_role`); registration + email verification; enable PostGIS, load barangay polygons, implement `ST_Contains` resolution service; retention policy written and the anonymization routine stubbed; **seed script generating 1,000 synthetic reports across all barangays** |
| **Mobile** | Expo project init; navigation skeleton; design system (colors, typography, components); API client with token refresh interceptor; login + register screens wired to the live API |
| **Web** | Vite + React + TS + Tailwind scaffold; routing with role-guarded routes; TanStack Query setup; API client; login screen wired to the live API; app shell (sidebar, header, role-aware nav) |
| **Thesis** | Ch. 2 RRL drafting begins; Ch. 3 system architecture + ERD sections written from the Sprint 0 artifacts |
| **Research** | LGU follow-ups; baseline instrument design; ethics revisions if requested |

**Owners:** to be assigned.

**Deliverables:** deployed API with auth on staging · migrated schema with PostGIS · barangay tagging service with passing tests · 1,000-report seed dataset · both client shells authenticating against the live API.

**DoD:** Global DoD + the RBAC test matrix passes for all three roles + `alembic upgrade head` runs clean on an empty database + barangay resolution verified against 10 known coordinates.

---

### 4.4 Sprint 2 — Report Intake (Mobile) & Admin Queue (Web) · **Weeks 5–6** (Oct 19 – Nov 1)

**Sprint goal:** A resident can submit a complete geotagged, photo-evidenced report from a phone, and an administrator can see it in a validation queue on the web. **This is the first end-to-end slice.**

**Stories:** US-03 (3), US-04 (5), US-05 (5), US-08 (8), US-09 (5) · **26 pts**

| Track | Tasks |
|---|---|
| **Backend** | `POST /reports` with Pydantic validation; presigned-upload flow to R2; transactional report + media creation; reference-number generator; `consents` endpoint and storage; `GET /admin/reports` with pagination, filters, and sorting; validate/reject endpoints with reason codes |
| **Mobile** | Privacy notice screen (EN + FIL) with explicit consent; 3-step submission wizard; category picker; description field with counter; camera + gallery via `expo-image-picker`; client-side image downscaling; upload with progress and retry; success screen showing the reference number |
| **Web** | Admin validation queue with thumbnails, filters, and sort; report detail view with photo lightbox and map preview; validate/reject actions with the reason modal; emergency-type banner |
| **Thesis** | Ch. 3 mobile module design; Ch. 3 privacy/ethics section; Ch. 2 RRL continues |
| **Research** | Baseline instruments finalized; ethics clearance expected in this window |

**Owners:** to be assigned.

**Deliverables:** working mobile submission flow · admin validation queue · consent audit records · end-to-end demo: phone → API → admin screen.

**DoD:** Global DoD + a report submitted on a **physical Android device** appears in the web queue with its photo and correct barangay within 5 seconds + consent is verifiably persisted server-side.

---

### 4.5 Sprint 3 — Location Capture, Categorization & Priority Scoring · **Weeks 7–8** (Nov 2 – Nov 15)

**Sprint goal:** Location capture is robust under poor GPS, and every validated report carries an explainable priority score that an administrator can defend.

**Stories:** US-06 (8), US-10 (3), US-11 (8), US-12 (5) · **24 pts**

| Track | Tasks |
|---|---|
| **Backend** | Priority scoring service implementing the Sprint 0 rubric; JSONB `priority_breakdown` persistence; category override endpoint retaining both values; override endpoint with mandatory reason; unit tests covering all four bands and boundary values; category weight and location sensitivity tables as seeded config |
| **Mobile** | `expo-location` integration; accuracy-radius display; 15 s timeout and 50 m accuracy fallback logic; `react-native-maps` manual pin with drag; nearest-landmark field; `location_source` + `accuracy_m` capture; permission rationale screens |
| **Web** | Category confirm/override control; priority panel rendering the "Why this score?" breakdown in plain language; override form with reason; priority band badges throughout the queue |
| **Thesis** | Ch. 3 priority algorithm section with the full rubric, weights, and worked examples; Ch. 3 web module design |
| **Research** | **Ethics clearance in hand**; baseline field collection begins (historical records + prospective logging setup) |

**Owners:** to be assigned.

**Deliverables:** GPS + manual-pin capture with fallback · deterministic scoring engine · explainability panel · override audit trail.

**DoD:** Global DoD + scoring unit tests cover all four bands and every boundary value + manual pin verified in a real low-signal location + the explainability panel reviewed by a non-technical person who can restate why a report scored as it did.

---

### 4.6 Sprint 4 — Assignment & Personnel Workflow · **Weeks 9–10** (Nov 16 – Nov 29)

**Sprint goal:** Reports flow from administrator to a named personnel member, who can act on them — the response half of the workflow exists.

**Stories:** US-13 (5), US-14 (5), US-15 (8), US-16 (3), US-38 (5) · **26 pts**

| Track | Tasks |
|---|---|
| **Backend** | Status state machine with server-enforced legal transitions (`409` on invalid); append-only `report_status_history` (no UPDATE/DELETE path); assignment endpoints with history preservation; `GET /personnel/reports` scoped to the assignee; office CRUD; personnel account creation/deactivation; office→category default mapping |
| **Mobile** | Status badge components matching the server enums; report detail scaffolding for the timeline (populated next sprint) |
| **Web** | Assignment modal (office → person); personnel work queue with priority/age sort and status filter; status update control offering only legal transitions; remark field on `IN_PROGRESS`; admin user & office management screens; 48-hour unassigned flag |
| **Thesis** | Ch. 3 workflow and state-machine documentation; Ch. 2 RRL first full draft due |
| **Research** | **Baseline field collection in progress** — prospective parallel logging live at the LGU receiving desk |

**Owners:** to be assigned.

**Deliverables:** complete assignment flow · personnel queue · enforced lifecycle with an append-only audit trail · office/personnel administration.

**DoD:** Global DoD + every invalid transition is rejected by the API and proven by test + a personnel account provably cannot see another's queue + assignment history survives reassignment.

---

### 4.7 Sprint 5 — Resolution, Notifications & Transparency · **Weeks 11–12** (Nov 30 – Dec 13)

**Sprint goal:** The loop closes — personnel document resolutions with evidence, and residents see progress without calling anyone.

**Stories:** US-17 (8), US-18 (5), US-19 (3), US-20 (8) · **24 pts**

| Track | Tasks |
|---|---|
| **Backend** | Resolution endpoint enforcing narrative + ≥1 after-photo; resolution media storage under the same access controls; notification dispatcher with a pluggable channel interface; Expo Push integration; Brevo email integration; in-app alert persistence; `notifications` table with delivery status; failures isolated from the triggering transaction |
| **Mobile** | Push token registration on login and clearing on logout; notification permission rationale; "My Reports" list; status timeline detail view showing office (never personal staff details); resolution view with before/after photos and pinch-zoom; pull-to-refresh; offline read cache; "Report still unresolved" → `REOPENED` |
| **Web** | Resolution upload form with multi-photo, narrative, completion date, and optional resources fields; in-app alert bell with unread count for personnel and administrators |
| **Thesis** | Ch. 3 notification architecture; Ch. 4 outline; screenshots captured for the manuscript |
| **Research** | Baseline collection continues; mid-collection quality check |

**Owners:** to be assigned.

**Deliverables:** resolution documentation with photo evidence · full status transparency on mobile · working push, email, and in-app notifications.

**DoD:** Global DoD + a push notification is confirmed received on a physical device within 30 s of a status change + `RESOLVED` is provably impossible without an after-photo + the complete lifecycle demo runs end to end: submit → validate → score → assign → in progress → resolve → resident sees resolution.

> **🏁 MILESTONE — End of Week 12: full core workflow demonstrable. This is the natural point for the mid-project / proposal defense.**

---

### 4.8 Semester Break · **Weeks 13–15** (Dec 14 – Jan 3) — reduced capacity

Not a sprint. Expect ~25% of normal capacity. Committed work only:

- Ch. 1–3 consolidated and submitted to the adviser for review (coordinator to be assigned; all contribute)
- Baseline data entry, cleaning, and preliminary descriptive analysis
- Defect backlog burn-down from Sprints 1–5 (whoever is available)
- Evaluation instrument drafting — SUS, TAM, D&M, ECT item pools
- **No new features.** Protecting this boundary is what makes the January sprints achievable.

---

### 4.9 Sprint 6 — Rating & Analytics Dashboard · **Weeks 16–17** (Jan 4 – Jan 17)

**Sprint goal:** Objective 5 becomes real — administrators can see the city, and residents can close the feedback loop.

**Stories:** US-21 (5), US-22 (8), US-30 (5), US-36 (3) · **21 pts** *(deliberately lighter — re-entry sprint after the break)*

| Track | Tasks |
|---|---|
| **Backend** | Rating endpoints with one-per-report and 7-day edit lock; auto-close job at 14 days; **SQL aggregation endpoints** for all dashboard widgets (never aggregate in the browser); barangay comparison query; filter parameters on all analytics endpoints; performance indexes |
| **Mobile** | Star rating UI with optional comment; rating edit within the window; report history search and filter; infinite scroll pagination |
| **Web** | Dashboard layout with KPI tiles; Recharts category bar, status donut, trend line, top-10-barangay bar; barangay comparison table with sortable columns; global filter bar (barangay, date range, category, status) with URL-encoded state and Clear All |
| **Thesis** | Ch. 3 analytics design; Ch. 4 results structure; **baseline preliminary findings written up** |
| **Research** | **Baseline analysis complete; as-is flowchart validated and signed by the LGU focal person** |

**Owners:** to be assigned.

**Deliverables:** resident rating flow · working analytics dashboard with city-wide and per-barangay views · **signed Baseline Report v1.0**.

**DoD:** Global DoD + the dashboard loads in under 3 s against the 1,000-report seed set + every widget respects every filter simultaneously + the Baseline Report is **locked and archived read-only**.

> **⛔ HARD GATE — End of Week 17: baseline dataset locked. Deployment cannot proceed before this.**

---

### 4.10 Sprint 7 — GIS Heatmaps, Exports & Duplicate Detection · **Weeks 18–19** (Jan 18 – Jan 31)

**Sprint goal:** The spatial and reporting capabilities that distinguish UGNAY from a simple ticket tracker.

**Stories:** US-29 (13), US-31 (8), US-32 (8) · **29 pts** *(the heaviest sprint — start the heatmap on day one)*

| Track | Tasks |
|---|---|
| **Backend** | `ST_SnapToGrid` density aggregation endpoint (~100 m cells) — **raw coordinates never leave the server in bulk**; `ST_DWithin` duplicate detection (100 m / same category / 7 days); duplicate linking with parent-child relations and `AffectedPeople` recalculation; PDF generation (WeasyPrint) and CSV export with a PII-inclusion flag that writes to the audit log |
| **Mobile** | Duplicate-suggestion notice ("a similar concern is already being handled") on the submission success screen |
| **Web** | Leaflet + react-leaflet map with OSM tiles; `leaflet.heat` density layer; barangay boundary overlay toggle; heatmap filter controls; PNG export for the manuscript; duplicate review side-by-side UI with link/dismiss; export UI with filter-aware options |
| **Thesis** | Ch. 3 GIS implementation; Ch. 4 figure preparation; **evaluation instruments finalized and content-validated by 3 evaluators** |
| **Research** | **Participant recruitment begins**; barangay captain endorsements secured; instruments pilot-tested on 5 respondents; Cronbach's α computed |

**Owners:** to be assigned.

**Deliverables:** GIS heatmap with filters · PDF/CSV administrative reports · duplicate detection and linking · validated evaluation instruments · 40+ pre-registered participants.

**DoD:** Global DoD + the heatmap renders 1,000 points in under 3 s + the network tab confirms no raw coordinate dump reaches the browser + exports honour the active filters and exclude PII by default + every instrument construct reaches α ≥ 0.70.

---

### 4.11 Sprint 8 — Hardening: Integration, Security & Privacy Review · **Weeks 20–21** (Feb 1 – Feb 14)

**Sprint goal:** The system is safe and stable enough to put in front of real residents and real city staff. **No new features.**

**Stories:** US-23 (8), US-26 (5), US-27 (3), US-37 (5), US-39 (5) · **26 pts**

| Track | Tasks |
|---|---|
| **Backend** | Server-side image normalization (1600 px cap, 300 px thumbnails, EXIF stripping); rate limiting on auth and submission endpoints; security headers; secret scanning in CI; audit logging for every PII read; verification that no endpoint leaks resident PII to non-admin callers; load test with k6 (50 concurrent users, 1,000 reports); query optimization and index review; automated DB backup configured |
| **Mobile** | EN/FIL localization of all strings including the privacy notice; device matrix testing (Android 8/11/14, low-RAM, no Play Services); crash handling; **Play Store internal testing track configured**; signed APK + written sideload instructions |
| **Web** | Cross-browser testing (Chrome, Edge, Firefox); responsive checks at 1366×768 and 1920×1080; error boundaries; session expiry handling; loading and empty states everywhere |
| **QA — the sprint's centre of gravity** | Full E2E suite across both clients (Playwright for web, Maestro or manual scripts for mobile); RBAC penetration matrix — every role attempts every forbidden action; **RA 10173 privacy compliance checklist walkthrough**; UAT scripts written for all three user groups; bug triage and fix |
| **Thesis** | Ch. 3 finalized; Ch. 4 methodology for evaluation; **privacy compliance checklist evidence compiled** |
| **Research** | Training materials for LGU staff; 3-minute onboarding video in Filipino; posters with QR codes; deployment runbook |

**Owners:** to be assigned.

**Deliverables:** hardened system · passing E2E suite · completed RA 10173 checklist · load test report · signed APK on the internal testing track · staff training materials · deployment runbook.

**DoD:** Global DoD + zero critical or high-severity defects open + the RBAC matrix shows no unauthorized access on any role/endpoint pair + the load test shows no 5xx at 50 concurrent users + the privacy checklist is complete with evidence for every item + **the adviser has signed off on deployment readiness**.

---

### 4.12 Sprint 9 — Pilot Deployment, Training & UAT · **Weeks 22–23** (Feb 15 – Feb 28)

**Sprint goal:** UGNAY is live in the pilot city with trained staff and onboarded residents. Deployment is the deliverable, not a side effect.

**Stories:** US-34 (5), US-35 (3), plus deployment and UAT work · **~20 pts** *(reserve half the sprint for deployment reality)*

| Track | Tasks |
|---|---|
| **Backend** | Production environment provisioning; production secrets and environment separation; automated backups verified by a **test restore**; monitoring and error alerting (Sentry free tier); production seed of real barangay boundaries, offices, and personnel accounts; go-live checklist |
| **Mobile** | Production build pointing at the production API; Play Store internal testing release; installation support materials; live push notification verification in production |
| **Web** | Production deployment; custom domain or a stable URL; admin and personnel accounts provisioned for real LGU staff; aging/SLA report; bulk assignment |
| **UAT** | Facilitated UAT sessions with each group: **administrators** (validate → categorize → score → assign, ~6 scenarios), **personnel** (queue → status → resolution upload, ~4 scenarios), **residents** (register → consent → submit → track → rate, ~5 scenarios). Record defects, time-on-task, and observations. Fix blocking defects within the sprint |
| **Training** | 2-hour admin/personnel training session at the city hall; quick reference cards; a named support contact and response commitment for the pilot |
| **Thesis** | Ch. 4 deployment documentation; UAT results written up; screenshots and figures finalized |
| **Research** | **Staged launch**: 5 barangays Week 22 → city-wide Week 24; barangay orientation sessions; poster and QR distribution |

**Owners:** to be assigned.

**Deliverables:** **live production system** · trained LGU staff · UAT reports for all three groups · onboarded residents · monitoring and verified backups.

**DoD:** Global DoD + the system is live and accessible to real users + every UAT blocking defect is resolved + staff have completed training and can operate unaided + a backup restore has been successfully tested + the support channel is active.

> **🏁 MILESTONE — Week 23: pilot live city-wide.**

---

### 4.13 Sprint 10 — Pilot Operation (Weeks 1–2) & Support · **Weeks 24–25** (Mar 1 – Mar 14)

**Sprint goal:** The pilot runs, the team supports it without disrupting it, and real data accumulates.

**Stories:** no new feature stories. Support, monitoring, and data collection.

| Track | Tasks |
|---|---|
| **Support** | Daily monitoring of error rates, notification delivery, and submission volume; a defect triage rota so one named person is on call each day; **hotfixes only** — no feature changes during the pilot; Expo OTA updates for mobile fixes so residents need not reinstall |
| **Observation** | Structured observation logs at the LGU; weekly check-ins with administrators and personnel; issue log capturing every support request and its cause |
| **Data** | Continuous system-log metric extraction; report-volume tracking against the 60-report floor |
| **Recruitment** | Ongoing resident onboarding; barangay reporting clinics if volume is short |
| **Thesis** | Ch. 4 drafting from live data; Ch. 5 outline |
| **⚠️ Checkpoint (end of Week 25)** | **C3 trigger review**: fewer than 30 reports or fewer than 15 pre-registered respondents → activate reporting clinics immediately |

**Owners:** all five on a support rota; data-capture and LGU-liaison leads to be assigned.

**Deliverables:** stable 2-week operation · observation logs · issue log · interim metric extract · mid-pilot checkpoint decision documented.

**DoD:** system uptime ≥ 95% over the two weeks + every support request logged with cause and resolution + no unresolved critical defect older than 48 h + the checkpoint decision is recorded in writing.

---

### 4.14 Sprint 11 — Pilot Operation (Weeks 3–4) & Evaluation Data Collection · **Weeks 26–27** (Mar 15 – Mar 28)

**Sprint goal:** The pilot completes and every piece of evaluation data is in hand. After this sprint, no new data can be collected.

| Track | Tasks |
|---|---|
| **Support** | Continued monitoring and hotfix-only support through Week 27 |
| **Evaluation — residents** | SUS + TAM + D&M + ECT + satisfaction instruments administered; on-site assisted sessions at barangay halls; target **n ≥ 30**, floor 20 |
| **Evaluation — personnel** | Instruments administered plus semi-structured interviews on workload change; target **n ≥ 8**, floor 5 |
| **Evaluation — administrators** | Instruments administered plus interviews on decision-making and the analytics dashboard; **time-and-motion re-measurement** mirroring the baseline protocol exactly; target **n ≥ 3**, floor 2 |
| **System metrics** | Extract all nine post-deployment metrics from system logs and the database using the same operational definitions as the baseline |
| **Privacy** | Final RA 10173 compliance checklist verification against the **production** system |
| **Thesis** | Ch. 4 results drafting; data cleaning and coding of open-ended responses |
| **End of Week 27** | **Pilot formally closes.** Data collection is closed. Residents are notified that the pilot period has ended and told how their reports will continue to be handled by the LGU. |

**Owners:** to be assigned.

**Deliverables:** complete evaluation dataset across three groups · post-deployment metrics extract · interview transcripts · completed privacy compliance checklist · pilot closure notice issued.

**DoD:** minimum sample sizes met or the shortfall formally documented with C3 applied + all nine metrics extracted using baseline-identical definitions + the anonymized research dataset is exported and contains no direct identifiers + the privacy checklist is complete with production evidence.

---

### 4.15 Sprint 12 — Analysis & Manuscript · **Weeks 28–29** (Mar 29 – Apr 11)

**Sprint goal:** Chapters 4 and 5 are written, and every claim in them is backed by a number the team can defend.

| Track | Tasks |
|---|---|
| **Statistical analysis** | Descriptive statistics for all constructs; normality checks (Shapiro–Wilk); baseline vs. system comparisons per §5.2 using the pre-specified tests; SUS scoring and interpretation per group; Cronbach's α re-computed on the final sample; effect sizes reported alongside every p-value; JASP or jamovi (both free) with outputs archived |
| **Qualitative analysis** | Thematic coding of open-ended survey responses and interview transcripts; triangulation against the quantitative findings |
| **Ch. 4** | Results and Discussion: system presentation with screenshots, baseline vs. system tables per metric, usability and acceptance results by group, TAM/D&M/ECT construct results, privacy compliance results, qualitative themes |
| **Ch. 5** | Summary, Conclusions, and Recommendations mapped one-to-one to the six objectives; limitations (including quasi-experimental design threats and any sample shortfall); Future Work drawn from the unbuilt Nice-to-Haves |
| **Technical docs** | System manual, installation guide, API documentation, database dictionary, source code appendices, deployment runbook |
| **Review** | Adviser review round; grammar and format checking; plagiarism/similarity check; complete reference list in the required style |

**Owners:** to be assigned.

**Deliverables:** complete statistical analysis with archived outputs · Ch. 4 and Ch. 5 drafts · full technical documentation · adviser-reviewed manuscript.

**DoD:** every measurable outcome in §5.2 has a computed result with a test statistic, p-value, and effect size + every objective has an explicit met/partially-met/not-met verdict with evidence + all chapters have passed one adviser review round + the similarity check is within institutional limits.

---

### 4.16 Final Phase — Defense Preparation · **Weeks 30–32** (Apr 12 – Apr 30)

| Week | Activity | Owner |
|---|---|---|
| 30 | Manuscript revisions from adviser feedback; final formatting; appendices assembled (instruments, consent forms, ethics clearance, LGU permission, code listings, raw data summaries) | All |
| 30 | Defense presentation deck (~20 slides); live demo script and a **recorded backup video** of the full workflow (never rely on live internet at a defense) | To be assigned |
| 31 | **Mock defense** with the adviser and a panel of peers; anticipated-questions drill covering methodology, statistics, privacy, scope limitations, and the priority algorithm | All |
| 31 | Revisions from mock defense; final manuscript printing and submission per institutional deadline | All |
| 32 | **FINAL DEFENSE**; post-defense revisions; final deposit; **turnover to the LGU** — system handover documentation, admin credentials, and a written statement of the post-pilot arrangement | All |

**Turnover note:** decide and document with the LGU before the defense whether the pilot system continues to operate, is archived, or is handed over. Residents who filed reports are owed an answer about what happens to their concerns — this is an ethical obligation, not a courtesy.

### 4.17 Milestone table & thesis chapter mapping

| # | Milestone | Target week | Date | Thesis chapters advanced |
|---|---|---|---|---|
| M1 | Project setup complete; LGU letters sent; ethics submitted | W2 | Oct 4 | **Ch. 1** complete; **Ch. 3** skeleton |
| M2 | Backend + auth live; city-wide seed data | W4 | Oct 18 | **Ch. 3** architecture, ERD |
| M3 | First end-to-end slice: mobile submit → web queue | W6 | Nov 1 | **Ch. 3** mobile design; **Ch. 2** drafting |
| M4 | Explainable priority scoring operational; **ethics clearance received** | W8 | Nov 15 | **Ch. 3** algorithm; **Ch. 2** continues |
| M5 | Assignment + personnel workflow; **baseline collection underway** | W10 | Nov 29 | **Ch. 3** workflow; **Ch. 2** full draft |
| M6 | **Core workflow complete end to end — proposal/mid-project defense** | W12 | Dec 13 | **Ch. 1–3** consolidated |
| M7 | Dashboard live; **⛔ baseline dataset LOCKED** | W17 | Jan 17 | **Ch. 3** analytics; **Ch. 4** baseline findings |
| M8 | GIS heatmap + exports; evaluation instruments validated | W19 | Jan 31 | **Ch. 3** final; **Ch. 4** methodology |
| M9 | Security & privacy review passed; deployment-ready | W21 | Feb 14 | **Ch. 3** locked; privacy checklist |
| M10 | **Pilot live city-wide; staff trained; UAT complete** | W23 | Feb 28 | **Ch. 4** deployment + UAT |
| M11 | **Pilot closes; all evaluation data collected** | W27 | Mar 28 | **Ch. 4** results data in hand |
| M12 | Analysis complete; **Ch. 4 and Ch. 5 drafted** | W29 | Apr 11 | **Ch. 4, Ch. 5** complete |
| M13 | Mock defense passed; manuscript submitted | W31 | Apr 25 | Full manuscript |
| M14 | **FINAL DEFENSE**; LGU turnover | W32 | Apr 30 | Defended |

**Chapter-to-sprint logic:**
- **Ch. 1** (Introduction, Objectives, Scope) — Sprint 0; revisited only if scope formally changes.
- **Ch. 2** (RRL, theoretical framework: TAM, DeLone & McLean, ECT, Agile) — drafted continuously Sprints 1–5, full draft by M5, finalized over the break.
- **Ch. 3** (Methodology, system design, architecture, ERD, algorithm, instruments, ethics) — written *as each component is built*, Sprints 0–8. Writing Ch. 3 after the fact is the most common cause of thesis-timeline collapse; this plan writes it in-sprint.
- **Ch. 4** (Results & Discussion) — structure from Sprint 6, baseline findings at M7, deployment/UAT at M10, full results Sprints 11–12.
- **Ch. 5** (Conclusions & Recommendations) — Sprint 12, mapped one-to-one against the six objectives.

### 4.18 Weekly timeline summary

| Weeks | Dates | Sprint | Focus | Key gate |
|---|---|---|---|---|
| 1–2 | Sep 21 – Oct 4 | **S0** | Setup, design, LGU letters, ethics submission, spikes | Ethics submitted |
| 3–4 | Oct 5 – Oct 18 | **S1** | Backend foundation, auth, RBAC, PostGIS, seed data | API live on staging |
| 5–6 | Oct 19 – Nov 1 | **S2** | Mobile submission + admin validation queue | First E2E slice |
| 7–8 | Nov 2 – Nov 15 | **S3** | GPS/manual pin, categorization, priority scoring | **Ethics clearance** |
| 9–10 | Nov 16 – Nov 29 | **S4** | Assignment, personnel queue, status lifecycle | Baseline collection live |
| 11–12 | Nov 30 – Dec 13 | **S5** | Resolution docs, notifications, status transparency | **M6: core workflow** |
| 13–15 | Dec 14 – Jan 3 | *break* | Ch. 1–3 consolidation, baseline analysis, defect burn-down | Ch. 1–3 to adviser |
| 16–17 | Jan 4 – Jan 17 | **S6** | Rating, analytics dashboard, barangay filters | **⛔ Baseline LOCKED** |
| 18–19 | Jan 18 – Jan 31 | **S7** | GIS heatmap, exports, duplicate detection | Instruments validated |
| 20–21 | Feb 1 – Feb 14 | **S8** | Hardening, security, privacy review, localization | Deployment-ready sign-off |
| 22–23 | Feb 15 – Feb 28 | **S9** | Production deployment, staff training, UAT | **M10: pilot live** |
| 24–25 | Mar 1 – Mar 14 | **S10** | Pilot operation wks 1–2, support, monitoring | Mid-pilot checkpoint |
| 26–27 | Mar 15 – Mar 28 | **S11** | Pilot wks 3–4, evaluation data collection | **M11: pilot closes** |
| 28–29 | Mar 29 – Apr 11 | **S12** | Statistical analysis, Ch. 4 and Ch. 5 | Chapters drafted |
| 30–32 | Apr 12 – Apr 30 | *final* | Revisions, mock defense, **FINAL DEFENSE**, LGU turnover | **M14: defended** |

---

## 5. Expected Outcomes

### 5.1 Deliverables

**Software**
1. **UGNAY resident mobile application** (Android, React Native/Expo) — account creation, privacy consent, concern submission with photo and GPS/manual pin, status tracking, push notifications, resolution viewing, rating.
2. **UGNAY officials' web application** (React) — personnel module (assigned queue, status updates, resolution documentation with photo evidence) and administrator module (validation, categorization, explainable priority scoring, assignment, city-wide monitoring, analytics dashboard, GIS heatmaps, administrative reports).
3. **Shared REST API and application server** (FastAPI) with role-based authentication, serving both clients from one source of truth.
4. **PostgreSQL/PostGIS database** with barangay boundary layer, complete schema, migrations, and seed data.
5. **Deployed production environment** with controlled media storage, monitoring, and verified backups.

**Analytics and reporting**
6. City-wide and per-barangay **analytics dashboard** (counts, categories, locations, status, resolution trends, ratings).
7. **GIS heatmap** with category, status, priority, and date filters and barangay boundary overlay.
8. **Exportable administrative reports** (PDF and CSV), filter-aware and PII-safe by default.

**Documentation**
9. **Source code** in a version-controlled repository with commit history evidencing Agile iteration.
10. **Technical documentation** — system manual, installation and deployment guide, API documentation (OpenAPI), data dictionary, ADR set.
11. **User documentation** — resident quick-start (EN/FIL), personnel guide, administrator guide, training materials, onboarding video.

**Research**
12. **Thesis manuscript, Chapters 1–5**, with appendices: evaluation instruments, consent forms, ethics clearance, LGU permission, baseline report, raw data summaries, code listings.
13. **Baseline Report v1.0** — validated as-is process map and nine baseline metrics, signed by the LGU focal person.
14. **Completed RA 10173 privacy compliance checklist** with production evidence.
15. **Anonymized research dataset** suitable for archival and verification.

### 5.2 Measurable outcomes

Design: **quasi-experimental, one-group pretest–posttest**. Given expected small and non-normal samples, non-parametric tests are the default; parametric equivalents are used only where normality is confirmed by Shapiro–Wilk (p > 0.05). Every comparison reports an **effect size** alongside its p-value. Significance level α = 0.05.

| # | Metric | Baseline measure (manual process) | System measure (UGNAY) | Comparison method & test | Target |
|---|---|---|---|---|---|
| **1** | **Time to submit a concern** | Time-and-motion of walk-in/call: travel + queue + narration + recording, in minutes (n ≥ 30 observations or recall interviews) | App timestamp from submission start to server acknowledgement, in minutes (system log, all pilot reports) | Independent samples; **Mann–Whitney U**, effect size **Cliff's δ**; t-test if normal | ≥ 60% reduction in median |
| **2** | **Submission-to-assignment time** | Elapsed time from receipt to endorsement to a responding office, from logbooks/parallel logging, in hours (n ≥ 30) | `created_at` → first `ASSIGNED` status history entry, in hours | **Mann–Whitney U**, Cliff's δ | ≥ 50% reduction in median |
| **3** | **Status visibility** | % of reports for which the resident could obtain a status without initiating contact (expected ≈ 0%) | % of reports with a resident-viewable status history (expected 100% by design) | **Two-proportion z-test**; report as a descriptive design outcome, since 100% is structural | ≥ 95% |
| **4** | **Report completeness** | % of records containing all of: category, specific location, description, and photographic evidence (from records review, n ≥ 50) | % of pilot reports with all four fields present | **Two-proportion z-test**, effect size **Cohen's h** | ≥ 90% |
| **5** | **Untraceable reports** | % of sampled reports that could not be located or whose outcome could not be determined during records review | % of pilot reports without a complete, retrievable status history (expected 0% — append-only history) | **Two-proportion z-test**, Cohen's h | ≤ 2% |
| **6** | **Follow-up effort** | Mean number of resident-initiated follow-up contacts (visits/calls/messages) per report, from resident pre-survey and staff logs | Mean number of resident-initiated support contacts per report during the pilot, from the support issue log | **Mann–Whitney U**; or **Poisson regression** if count assumptions hold; effect size **rank-biserial r** | ≥ 70% reduction in mean |
| **7** | **Resolution documentation** | % of resolved concerns with any written record of the action taken, and % with photographic evidence (records review) | % of `RESOLVED` reports with an action narrative and ≥ 1 after-photo (100% enforced by the API) | **Two-proportion z-test**, Cohen's h | ≥ 95% |
| **8** | **Resident satisfaction** | Pre-survey Likert 1–5 satisfaction with the current reporting process (n ≥ 30 residents) | Post-pilot satisfaction Likert 1–5 plus the mean resolution rating (1–5 stars) from in-app ratings | **Mann–Whitney U** (independent) or **Wilcoxon signed-rank** if the same residents are surveyed twice; effect size r | Mean ≥ 4.0/5.0; ≥ 1.0 point improvement |
| **9** | **Administrative workload** | Time-and-motion: minutes of staff time per concern for receiving, recording, endorsing, and tracking (n ≥ 20 observations across ≥ 3 staff) | Re-measurement using the identical protocol during the pilot, same staff where possible | **Wilcoxon signed-rank** (paired, same staff) or Mann–Whitney U; effect size r | ≥ 40% reduction in median minutes per concern |

**Supporting system-generated measures** (descriptive, no baseline comparison): total reports by category and barangay; median resolution time by category and by priority band; priority override rate (an indicator of algorithm acceptance); duplicate detection precision; GPS vs. manual-pin usage split and accuracy distribution; notification delivery success rate; p95 API latency.

### 5.3 Evaluation instruments

All instruments are content-validated by the adviser plus two faculty/IT evaluators, pilot-tested on 5 respondents, and reported with Cronbach's α per construct (threshold α ≥ 0.70).

| Instrument | Constructs / items | Residents | Personnel | Administrators |
|---|---|---|---|---|
| **SUS** (Brooke, 1996) | 10 standard items, 5-point scale, scored 0–100 | ✔ mobile app | ✔ web app | ✔ web app |
| **TAM** (Davis, 1989) | Perceived Usefulness (4 items), Perceived Ease of Use (4), Behavioral Intention (3), 5-point Likert | ✔ | ✔ | ✔ |
| **D&M IS Success** (DeLone & McLean, 2003) | System Quality (4), Information Quality (4), Service Quality (3), Use (2), User Satisfaction (3), Net Benefits (4) | ✔ | ✔ | ✔ (Net Benefits emphasizes decision support) |
| **ECT** (Oliver, 1980; Bhattacherjee, 2001) | Confirmation (3), Satisfaction (3), Continuance Intention (3) — measured post-use | ✔ | ✔ | ✔ |
| **Process satisfaction** | Custom 5-point items on the reporting/response experience; administered **pre** (baseline) and **post** | ✔ | ✔ | ✔ |
| **Semi-structured interview** | Workload change, decision-making support, perceived barriers, willingness to continue | — | ✔ (n ≥ 5) | ✔ (all) |
| **Time-and-motion protocol** | Identical observation sheet used at baseline and post-deployment | — | — | ✔ |

**Target samples:** residents n ≥ 30 (floor 20) · personnel n ≥ 8 (floor 5) · administrators n ≥ 3 (floor 2). All three groups are reported separately; results are never pooled across roles.

**Data privacy compliance checklist** — applied twice (Sprint 8 pre-deployment against staging, Sprint 11 against production), structured on RA 10173 and NPC guidance:

| Principle | Checklist items (evidence required for each) |
|---|---|
| **Transparency** | Privacy notice present, in plain language, in EN and FIL · states collection, purpose, recipients, retention, and data-subject rights · consent recorded with policy version and timestamp · re-consent on policy change |
| **Legitimate purpose** | Every collected field is traceable to a stated processing purpose · no secondary use without consent · research analysis uses only anonymized/aggregated data |
| **Proportionality** | No field collected that the workflow does not require (verified field-by-field against the data dictionary) · EXIF stripped · heatmap serves aggregated grid cells, never raw coordinates · precise residential locations never publicly exposed |
| **Security — organizational** | Roles defined and documented · access restricted by role · breach response procedure written with a named LGU contact · team members briefed |
| **Security — technical** | HTTPS enforced · argon2 password hashing · JWT with short expiry and refresh rotation · presigned short-lived media URLs · bucket listing disabled · secrets in environment variables with CI secret scanning · rate limiting on auth and submission |
| **Security — physical** | Managed cloud hosting with the provider's controls documented · no PII on personal devices or in the repository · local research data encrypted |
| **Data subject rights** | In-app account deletion request · access to one's own data · correction path via support · rights stated in the privacy notice |
| **Retention & disposal** | Written retention schedule · anonymization routine implemented and tested · deletion actioned within 30 days |
| **Accountability** | Audit log of every PII read with actor and timestamp · append-only status history · designated team privacy focal person (to be assigned) |

### 5.4 Success criteria

The project is judged against four tiers. **Tier 1 must be fully met for the thesis to succeed.**

**Tier 1 — Must be met (non-negotiable)**
1. All **28 Must-Have user stories** are implemented and demonstrated on the deployed system.
2. Both clients are functional: residents can complete the full submission-to-rating cycle on mobile; personnel and administrators can complete the full validation-to-resolution cycle on web.
3. The complete workflow operates end to end in production: submit → validate → categorize → score → assign → act → document resolution → notify → rate → analyze.
4. The pilot ran for **at least 4 weeks** with **at least 60 genuine reports** processed to completion.
5. All **nine baseline metrics** were collected before deployment and re-measured after, with documented comparison results.
6. Evaluation minimums met: **≥ 20 residents, ≥ 5 personnel, ≥ 2 administrators**.
7. The **RA 10173 compliance checklist is fully satisfied** with evidence, and **no data privacy incident occurred** during the pilot.
8. **Chapters 1–5 are complete** and the thesis is successfully defended.

**Tier 2 — Strong project**
9. **SUS ≥ 68** ("above average") for each of the three user groups, with a target of **≥ 70**.
10. **Statistically significant improvement (p < 0.05)** on at least **5 of the 9** baseline metrics, with at least a medium effect size on three of them.
11. Mean resident satisfaction **≥ 4.0/5.0**; mean resolution rating **≥ 4.0/5.0**.
12. TAM Perceived Usefulness and Behavioral Intention means **≥ 4.0/5.0** across all groups.
13. All evaluation constructs reach **Cronbach's α ≥ 0.70**.
14. GIS heatmap and exportable administrative reports are delivered and used by administrators during the pilot.

**Tier 3 — Excellent project**
15. Improvement on **8 of 9** metrics, with reduction targets in §5.2 met.
16. **≥ 80%** of Should-Have stories delivered.
17. The LGU expresses written intent to continue using or adopting the system after the pilot.
18. The system processed **≥ 150 reports** with **≥ 70%** reaching `RESOLVED` within the pilot.
19. p95 API latency under 2 s sustained throughout the pilot with ≥ 99% uptime.

**Explicit failure conditions** (any of these means the project did not meet its objectives, and should be stated honestly rather than obscured): a Must-Have story undelivered; no baseline collected before deployment; a privacy incident exposing resident data; fewer than 20 total evaluation respondents; the system never deployed to real users.

### 5.5 Expected contributions

**Theoretical**
- Provides empirical evidence for **TAM** in a Philippine LGU e-governance context across **three distinct user roles** with asymmetric motivations — residents (voluntary use, service-seeking), personnel (mandated use, workload-affected), administrators (decision-support use). Most TAM studies examine a single homogeneous user group; role-differentiated acceptance in a mandatory-plus-voluntary mixed setting is thinly covered.
- Applies the **DeLone & McLean IS Success Model** to a two-client system sharing one backend, allowing System Quality and Information Quality to be assessed for the same information served through two different interfaces — a configuration the original model does not explicitly address.
- Tests **Expectation-Confirmation Theory** in a civic-participation setting where confirmation is shaped not only by the software but by the *government's actual response*, separating system satisfaction from service satisfaction — a distinction that matters for any transparency platform and is rarely disentangled.
- Documents **Agile practice under academic constraints** — fixed non-negotiable deadlines, part-time capacity, an external stakeholder gate, and a parallel research track — contributing to the literature on Agile adaptation in student and resource-constrained contexts.

**Practical**
- Delivers a **working, low-cost, city-level system** that Philippine LGUs can evaluate or adopt, built entirely on free and open-source components with a documented monthly operating cost near zero — directly addressing the affordability barrier that keeps smaller cities off commercial civic-tech platforms.
- Contributes an **explainable, rule-based priority scoring rubric** with published weights, factor scales, and band thresholds. Because it is transparent and non-ML, it is auditable by officials and defensible to residents — a practical requirement in public administration that opaque scoring cannot meet.
- Provides a **documented integrated workflow** spanning prioritization, assignment, resolution documentation, resident feedback, and analytics — the specific gap left by DILG Online Sumbungan, eGovPH eCMS, and Marikina e-Concern.
- Supplies **baseline measurement instruments and a nine-metric framework** that other LGUs or researchers can reuse to assess their own manual concern-handling processes, independently of UGNAY.
- Demonstrates a **PostGIS-based barangay auto-tagging pattern** that makes city-wide geographic analytics achievable without resident-entered location metadata — a reusable technique for any Philippine LGU system operating across barangay boundaries.

**To future researchers**
- Establishes a **replicable quasi-experimental protocol** for evaluating civic reporting systems against a manual baseline, with the instruments, operational metric definitions, and statistical approach published in the appendices.
- Publishes **anonymized pilot data** on report volumes, category distributions, spatial patterns, and resolution times for a Philippine city — a scarce empirical resource for subsequent urban-informatics and e-governance research.
- Identifies a concrete **Future Work agenda** grounded in what this pilot could not do: multi-city generalization, iOS coverage, SMS channels for residents without smartphones, ML-assisted categorization benchmarked against this rule-based baseline, integration with eGovPH eCMS, longitudinal continuance measurement beyond a 4-week pilot, and accessibility for low-literacy and low-vision users.
- Documents **honest negative and partial findings** — where the system did not improve a metric, where adoption lagged, and where the priority algorithm was overridden by administrators — which are more useful to the next research team than a uniformly positive report.

---

## 6. Inconsistencies & Open Questions to Resolve

These are gaps or contradictions in the project description that should be settled with your adviser before Sprint 1. They are ordered by how much damage they cause if left unresolved.

1. **⚠️ Database contradiction: MySQL vs. PostgreSQL.** Your brief specifies **MySQL**, but you selected **PostgreSQL + SQLAlchemy ORM**. These are incompatible claims in a manuscript. SQLAlchemy also implies a **Python** backend (FastAPI), not Laravel/Node. **Recommendation:** go with PostgreSQL + PostGIS — it makes barangay point-in-polygon tagging and heatmap aggregation one-line SQL instead of weeks of custom work — and **update Chapter 3 and any approved proposal accordingly**. If your proposal has already been defended with MySQL specified, confirm with your adviser whether a technology change requires re-approval. *Do not leave both in the document.*

2. **⚠️ Objective 1 requires city records, but "no integration with city information systems" is out of scope.** These are different things (manual records access vs. system integration), but a panelist will ask. Clarify explicitly: you need **read access to existing logbooks, call logs, and endorsement records for baseline measurement only** — no technical integration. Put this in the LGU permission letter in exactly those words, and state the distinction in Ch. 3.

3. **⚠️ The pilot city is unnamed.** Nearly everything downstream depends on it: barangay count, boundary data availability, office structure, staff numbers, resident population, and baseline record quality. **This must be settled by Week 6** (the R1 decision point). Approach three cities in parallel starting Week 1.

4. **Emergency reports have no defined handling rule.** "Does not replace emergency hotlines" is stated, but the workflow has no gate for it. A resident *will* submit an active fire, a live electrical wire, or a medical emergency. **Decide now:** (a) a prominent in-app warning before submission with hotline numbers; (b) certain categories trigger an immediate high-visibility admin alert; (c) a `REJECTED — emergency, referred to hotline` reason code. This plan assumes all three; confirm it is acceptable to the LGU, because it carries real liability implications.

5. **What happens when a resident disputes a resolution?** The brief specifies resident rating but defines no state transition for "this was not actually fixed." A 1-star rating on a `RESOLVED` report is a workflow signal with no defined handler. This plan assumes a `REOPENED` state, limited to one use per report, escalating to an administrator on a second dispute. **Confirm this is the behavior you want** — it materially affects resolution-time metrics (does the clock restart?).

6. **`AffectedPeople` in the priority formula has no reliable source.** If residents self-report it, it will be inflated and will not be comparable across reports. **Options:** (a) administrator-assessed during validation — reliable but adds admin workload; (b) derived from linked duplicate count — objective but depends on US-32, currently only a Should-Have; (c) derived from the barangay population density of the report location — objective and free. **Recommendation:** administrator-assessed with a documented rubric (1 = individual/household, 3 = street/purok, 5 = barangay-wide or a major thoroughfare), since Objective 3 already states administrators make the final decision. **Note the dependency:** if duplicate detection (US-32) is cut under contingency C2, option (b) disappears — decide before Sprint 3.

7. **iOS is unaddressed.** The brief says "mobile application" without naming a platform. iOS requires a **$99/year Apple Developer account** and a Mac for builds — likely outside a student budget. This plan targets **Android-first** and lists iOS as Future Work. **Confirm this is acceptable**, and note that it biases the resident sample toward Android users — a limitation for Ch. 5.

8. **Is there any public-facing view?** The privacy requirements imply there might be ("do not expose resident names... publicly"), but no Must-Have story creates a public feed. Currently, only the reporting resident, assigned personnel, and administrators see any report. **Confirm:** is a public or anonymized view of open concerns required, or is US-40 (Nice-to-Have) the only place this appears? This affects the privacy notice wording, which must be written accurately in Sprint 0.

9. **"Personnel" is undefined — city office staff, barangay staff, or both?** This changes the account provisioning model, the assignment routing, the training plan, and the personnel sample size. If barangay-level staff are included across 20–30 barangays, the training and account-management burden grows substantially. **Recommendation for feasibility:** limit personnel to **city office staff in 4–6 responding offices** for the pilot, and state barangay-level personnel as Future Work.

10. **Pilot duration was never specified.** This plan assumes **4 weeks**, which is the practical minimum for generating enough reports to analyze while leaving time for analysis and writing. Shorter risks an insufficient sample; longer squeezes Chapters 4 and 5. **Confirm 4 weeks with your adviser.**

11. **The statistical design has a confounding problem you should name before a panelist does.** Comparing pre- and post-periods means comparing *different report populations* at *different times*, with novelty effects, seasonal variation (rainy vs. dry season affects drainage and flooding reports enormously), and possible staffing changes. **Do not present this as a controlled experiment.** Declare it as **quasi-experimental one-group pretest–posttest**, name history, maturation, and novelty as threats to internal validity in Ch. 3, and address them again in Ch. 5 limitations. Handled openly, this is a strength; discovered by the panel, it is a weakness.

12. **Barangay boundary data availability is unverified.** The entire city-wide tagging and per-barangay analytics design rests on having boundary polygons. **Verify in Sprint 0** whether PhilGIS or PSA shapefiles exist for your pilot city at usable quality. If not, budget ~12 hours to digitize them in QGIS from a city planning map. This is a Sprint 0 spike for a reason — discovering it in Sprint 6 would be costly.

13. **Metric 3 (status visibility) is structurally 100% by design, not an empirical finding.** Reporting "0% → 100%, p < 0.001" will look naive to a panel. Present it as a **design outcome** (the system makes status visibility structural) and measure the *behavioral* consequence instead — metric 6 (follow-up effort), which is the real-world effect of visibility. The same caution applies to metrics 5 and 7, which are also enforced by design rather than emergent.

14. **Who operates the system after the pilot ends?** Residents will have filed genuine concerns about real problems. Whether the LGU continues, the system is archived, or reports are handed back manually, **this must be agreed in writing before launch and communicated to residents at pilot closure.** It is an ethics-committee question as much as a project-management one, and it is easier to answer in Week 22 than in Week 28.

---

## Verification

How to confirm this plan is working, at each level:

**Per sprint** — the Global Definition of Done (§4.0) is checked story-by-story by a member other than the author before the sprint review. A sprint is not "done" because the code exists; it is done when it runs on staging and a second person has verified each acceptance criterion.

**Per milestone** — each of M1–M14 has a single binary test:
- M3/M6: the **end-to-end demo runs on staging in front of the whole team**, from a physical Android phone through to the web dashboard, without a developer touching the database.
- M7: the baseline dataset file is **archived read-only with a version stamp** — verifiable by its existence and immutability.
- M9: the RBAC matrix and privacy checklist are complete documents with evidence per row, adviser-signed.
- M10: a **real LGU staff member, unaided, completes a full validation-to-assignment cycle** on production.

**Technical verification throughout**
- CI runs lint + unit tests on every PR; `main` is protected and cannot be pushed to directly.
- `alembic upgrade head` on an empty database must succeed at every sprint boundary — this is what guarantees the system can be rebuilt for the defense.
- E2E suite (Playwright for web, scripted mobile runs) executes the full lifecycle before every deployment.
- Load test (k6, 50 concurrent users, 1,000 reports) re-run in Sprint 8 and again before the pilot.
- The RBAC penetration matrix — every role attempting every forbidden action — must show zero unauthorized access.

**Research verification**
- Baseline instruments are pilot-tested on 5 respondents before full collection, and the as-is process map is signed by the LGU focal person — not just shown to them.
- Cronbach's α computed per construct at both pilot-test and final-sample stages.
- Post-deployment metrics use **byte-identical operational definitions** to the baseline; write these definitions down in Sprint 0 and do not revise them after data collection begins.
- Statistical outputs archived from JASP/jamovi so any number in Ch. 4 can be traced back to its source.

**Final verification** — the defense demo runs from a clean environment, with a **pre-recorded backup video** of the complete workflow. Never depend on venue internet.
