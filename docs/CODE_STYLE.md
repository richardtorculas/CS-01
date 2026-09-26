# Code Style

## General

- Prefer clear names over comments. Comment *why*, not *what*.
- Keep functions small and single-purpose. Keep files under ~300 lines; split when they grow.
- No dead code, commented-out code, or unused imports in merged PRs.
- English for code and comments. User-facing strings go through i18n (mobile) so Filipino can be added.

## Python (`api/`)

- Python 3.12, formatted and linted with **ruff** (`ruff format`, `ruff check`). Line length 100.
- Type hints on every function signature. SQLAlchemy 2.0 typed style (`Mapped[...]`, `mapped_column`).
- Naming: `snake_case` functions and variables, `PascalCase` classes, `UPPER_SNAKE` constants.
- Follow the layer rules in [ARCHITECTURE.md](ARCHITECTURE.md): no queries in routers, no HTTP concepts in services.
- Raise domain exceptions in services (e.g. `InvalidTransitionError`); translate them to HTTP errors in one exception handler.
- Tests with **pytest**. Name tests `test_<behavior>_<condition>`, e.g. `test_transition_rejected_when_status_closed`.

## TypeScript (`web/`, `mobile/`)

- TypeScript `strict` mode. No `any`; use `unknown` and narrow.
- Linted with **eslint**, formatted with **prettier**. `tsc --noEmit` must pass.
- Function components and hooks only.
- Naming: `PascalCase` components and their files (`ReportCard.tsx`), `camelCase` functions and hooks (`useReports`), `UPPER_SNAKE` constants.
- Server data via TanStack Query hooks in `src/hooks/`; API calls in `src/api/`. Components don't call `fetch`.
- API types are generated from the OpenAPI spec, not written by hand.
- Web styling with Tailwind utility classes using the tokens in [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md); no inline hex colors.

## Git

- Branches: `feature/US-XX-short-name`, `fix/short-name`, `docs/short-name`, `chore/short-name`.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/) with the story ID, e.g. `feat(api): enforce status transitions (US-15)`.
- Never push directly to `main`. Every PR needs one approving review from another member and green CI.
- Keep PRs small (aim for under ~400 changed lines). Describe what changed, why, and how it was tested.
