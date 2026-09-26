# PRD — UGNAY

Condensed product requirements for day-to-day development. The source of truth for full acceptance criteria, schedule and research design is [UGNAY-Project-Plan.md](UGNAY-Project-Plan.md).

## Problem

In Philippine city governments, resident concerns (damaged roads, clogged drainage, uncollected garbage, broken streetlights) arrive through walk-ins, phone calls and private messages. Nothing categorizes, prioritizes, assigns or tracks them to a documented resolution. Residents can't see progress, reports get lost when a staff member is unavailable, and administrators have no city-wide picture.

## Product

A city-level, low-cost system covering the full life of a concern:

> Report + evidence + location → validation → categorization → priority → assignment → action → resolution evidence → status transparency → resident feedback → analytics

## Users

| Role | Client | Core jobs |
|---|---|---|
| Resident | Mobile | Register, consent to privacy notice, submit a geotagged report with photos, track status, view resolution, rate it |
| Personnel | Web | Work an assigned-concern queue, update status, document resolution with photos |
| Administrator | Web | Validate, categorize, review priority score, assign, monitor city-wide, view dashboard and heatmaps, export reports, manage personnel and offices |

## Must-have features

| Area | Stories |
|---|---|
| Accounts, RBAC, consent | US-01, US-02, US-03 |
| Report submission (category, description, photos, GPS/manual pin) | US-04 – US-06, US-08 |
| Barangay auto-tagging (PostGIS) | US-07 |
| Validation, categorization, priority scoring and override, assignment | US-09 – US-13 |
| Personnel queue, status lifecycle, resolution documentation | US-14 – US-17 |
| Resident timeline, resolution view, notifications, rating | US-18 – US-21 |
| Analytics dashboard | US-22 |
| Privacy, performance, consistency, retention | US-23, US-26 – US-28 |

Should-have: heatmap, dashboard filters, PDF/CSV export, duplicate detection, offline drafts, aging reports, bulk assign, image normalization, personnel management, English/Filipino (US-29 – US-39).

## Status lifecycle

`SUBMITTED → VALIDATED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`
`REJECTED` from `SUBMITTED`; `REOPENED` from `RESOLVED`. Enforced server-side (US-15).

## Success measures

- A resident completes a submission in under 3 minutes.
- Every report has an append-only, timestamped history ending in documented resolution.
- p95 API latency under 2 s (lists/details), under 5 s (submission with one image).
- Post-pilot metrics improve over the manual-process baseline (evaluated in the research track).

## Out of scope

More than one pilot city · complaints against officials · replacing emergency hotlines · integration with eGovPH eCMS or other city systems · machine-learning prioritization · guaranteeing resolution · offline operation beyond drafts · iOS release.
