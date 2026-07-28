from datetime import UTC, datetime

from learn_fastapi.src.shared.application.security import Clock


class SystemClock(Clock):
    """Clock adapter backed by the system UTC time."""

    def now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(tz=UTC)
