from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator


def _to_utc(value: datetime) -> datetime:
    # Naive values (SQLite) are already UTC; aware ones (Postgres session zone) are converted.
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


# API.md: timestamps are ISO 8601 in UTC, whatever zone the database session uses.
UtcDatetime = Annotated[datetime, AfterValidator(_to_utc)]
