# CS-01 — UGNAY

Community issue reporting and government response system. See [AGENTS.md](AGENTS.md) for the repository layout and rules, and [docs/](docs/) for requirements and conventions.

## Getting started (API)

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) and, if you will edit or test the API code, [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs the right Python version and creates the virtualenv for you, so there is no manual venv setup.

**Just run the API** (mobile/web developers): Docker only.

```bash
docker compose up --build      # Postgres + API with migrations applied
```

The API is at <http://localhost:8000> (interactive docs at `/docs`). Code changes in `api/` reload automatically.

**Work on the API code** (backend developers): run only the database in Docker, and the API on your machine.

```bash
docker compose up -d db
cd api
cp .env.example .env           # values already match the compose database
uv sync                        # creates api/.venv from the lockfile
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Checks** (run from `api/`, the same ones CI will run):

```bash
uv run ruff check . && uv run ruff format --check .
uv run pytest                  # SQLite by default
TEST_DATABASE_URL=postgresql+psycopg://ugnay:ugnay@localhost:5432/ugnay uv run pytest   # against Postgres
```

Open `api/` in your editor and select `api/.venv` as the Python interpreter.

**Changing dependencies:** `uv add <package>` (or `uv add --dev <package>`), then commit both `pyproject.toml` and `uv.lock`. Never edit `uv.lock` by hand.

**Reset the local database:** `docker compose down -v` (deletes the volume).

## Troubleshooting

- **Port 5432 already in use:** you have a local Postgres running. Stop it, or change the left side of `"5432:5432"` in `docker-compose.yml` (and `DATABASE_URL` in `api/.env`).
- **`docker compose` cannot connect:** start Docker Desktop and wait until it reports it is running.
