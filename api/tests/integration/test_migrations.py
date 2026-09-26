from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from app.core.config import get_settings
from app.db.base import Base


def test_migrations_run_on_fresh_database_and_match_models(tmp_path, monkeypatch):
    """A fresh DB upgraded to head must have no drift from the models (DoD: fresh-DB migration)."""
    url = f"sqlite:///{tmp_path / 'fresh.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    try:
        command.upgrade(Config("alembic.ini"), "head")
        engine = create_engine(url)
        with engine.connect() as connection:
            diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
        engine.dispose()
    finally:
        get_settings.cache_clear()
    assert diff == []
