# Security and Privacy

UGNAY handles resident personal data and must comply with the Data Privacy Act of 2012 (RA 10173). These rules are mandatory for every change.

## Authentication

- JWT access token: 15 minutes. Refresh token: 7 days, rotated on use (the used token is invalidated).
- Passwords hashed with argon2; minimum 8 characters; never returned in any response or logged.
- Residents must verify email (or SMS OTP) before their first report.
- Personnel and administrator accounts are created **only** by an administrator. There is no public officials' signup.
- Mobile stores tokens in `expo-secure-store`, never in AsyncStorage.

## Authorization (RBAC)

| Role | Can | Cannot |
|---|---|---|
| Resident | Manage own profile, create and view own reports, rate own resolved reports | Access any `/admin/*` or `/personnel/*` endpoint; see other residents' reports |
| Personnel | View and update reports assigned to them; upload resolution evidence | Validate, score, assign; see resident contact details |
| Administrator | Everything above plus validation, categorization, priority override, assignment, analytics, exports, user/office management | Delete status history |

- Enforce roles with FastAPI dependencies on every protected route. UI hiding is not security.
- Ownership checks (e.g. "is this my report / my assignment") happen in the service layer.
- The RBAC test matrix (3 roles × every protected endpoint) runs in CI and must stay green.

## Personal data

- Collect only: name, mobile, email, barangay, hashed password, timestamps. No address, birthdate or ID numbers.
- Resident name, mobile, email and home coordinates are returned **only** to administrators, and every read is written to `audit_logs` (actor, target, timestamp).
- Residents see the acting **office**, never an individual staff member's personal details.
- Rating comments shown to admins mask the resident name to initials.
- Exports exclude personal data unless an admin explicitly opts in; the opt-in is audit-logged.
- Research datasets contain no direct identifiers.

## Consent

Record `{user_id, policy_version, timestamp, ip}` in `consents`. Re-prompt when `policy_version` increments. The consent checkbox is never pre-ticked.

## Media

- The storage bucket is private; listing is disabled.
- The database stores only object keys. Access is through presigned URLs valid for 15 minutes.
- Strip EXIF metadata server-side (keep only coordinates already stored on the report).
- Limit: 1–3 photos per report, 10 MB total per report.

## Secrets

- All secrets in environment variables. Commit `.env.example` with placeholder values only.
- CI secret scanning is enabled. If a secret is committed, rotate it immediately; deleting the commit is not enough.
- Credentials are shared through the team's secrets vault, never in chat or the repo.

## Logging

Never log passwords, tokens, resident contact details, or full request bodies of auth and report endpoints. Log IDs, not personal data.

## Transport

HTTPS everywhere. CORS allows only the known web origins.

## Retention

Reports and media are kept 2 years after closure, then media is purged and records are anonymized. Account deletion requests are actioned within 30 days. See US-28.

## Incident response

On a suspected breach: contain, notify the team's designated privacy contact (to be assigned) and the LGU contact, and follow the written breach-response procedure. RA 10173 requires notifying the National Privacy Commission within 72 hours of a qualifying breach.
