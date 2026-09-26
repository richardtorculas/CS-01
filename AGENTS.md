# AGENTS.md — Instructions for AI coding agents

UGNAY is a community issue reporting and government response system: a resident mobile app and an officials' web app over one shared REST API. Read the docs below before working in an area; don't guess conventions.

| Read before… | File |
|---|---|
| Any feature work (what and why) | [docs/PRD.md](docs/PRD.md) |
| Touching more than one layer or adding a service | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Adding or changing an endpoint | [docs/API.md](docs/API.md) |
| Changing models or migrations | [docs/DATABASE.md](docs/DATABASE.md) |
| Anything involving auth, roles, PII, media or secrets | [docs/SECURITY.md](docs/SECURITY.md) |
| Building UI (web or mobile) | [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) |
| Writing any code | [docs/CODE_STYLE.md](docs/CODE_STYLE.md) |

Full requirements and acceptance criteria: [docs/UGNAY-Project-Plan.md](docs/UGNAY-Project-Plan.md) §2 (user stories US-01 to US-47).

## Repository layout

- `api/` — FastAPI backend (routers → services → models)
- `mobile/` — React Native + Expo resident app (Android-first)
- `web/` — React + Vite + TypeScript officials' app
- `tests/` — cross-client E2E and load tests
- `docs/` — these docs, ADRs, design, research, manuscript

## Non-negotiable rules

1. **One source of truth.** Status transitions, priority scoring, validation rules and enums live in `api/app/services` and `api/app/core`. Clients never duplicate business logic; they read enums from the API (US-27).
2. **Server-side enforcement.** Permissions and status transitions are enforced by the API, never only in the UI.
3. **Privacy first.** Never log PII, never return resident contact details to non-admins, never expose a public media URL. See SECURITY.md.
4. **Stay in scope.** No machine-learning prioritization, no integration with external government systems, no iOS-specific work, no emergency-hotline features. See PRD.md "Out of scope".
5. **Schema changes go through Alembic.** Never edit the database by hand or modify an already-merged migration.
6. **No secrets in code.** Use environment variables; update `.env.example` when adding one.

## How to work

- Keep changes small and scoped to one user story. Reference the story ID (e.g. `US-15`) in commit messages and PR titles.
- Write or update tests with every backend change; business logic in services must have unit tests.
- When an API contract changes, update the Pydantic schemas (the OpenAPI spec regenerates from them) and note the change in the PR description.
- Record significant design decisions as a one-page ADR in `docs/adr/`.
- If a requirement is ambiguous, ask rather than invent behavior. Check the plan's Open Questions section first.

## Reporting back

When a task or ticket is finished, give a detailed explanation of the work, written so a teammate who did not watch it can follow:

- **What was done:** every task performed, grouped by area (code, database, tests, docs, tooling), with the files involved.
- **Why:** the reasoning behind each notable choice, including decisions the ticket did not specify. Mark these clearly as assumptions so the team can confirm or overturn them.
- **How it maps to the ticket:** state how each acceptance criterion was met and which test proves it.
- **What was verified and how:** the commands run and their results. Say plainly what was not run or could not be verified, and what failed and how it was fixed.
- **What remains:** follow-ups, out-of-scope items left for other stories, and anything the team must do next.

Do not summarize only the outcome, and do not claim something works without saying how it was checked.

## Definition of Done (summary)

Merged via reviewed PR · acceptance criteria met · CI green (ruff, pytest, eslint, tsc) · OpenAPI updated · migration runs on a fresh DB · no new secrets, PII in logs or public media paths · works on Android 8/11/14 and Chrome/Edge ≥1366×768. Full list: project plan §4.0.
