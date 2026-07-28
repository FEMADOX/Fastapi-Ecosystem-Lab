from datetime import UTC, datetime, timedelta
from uuid import uuid4

from learn_fastapi.src.auth.application.commands import (
    CreateRefreshTokenCommand,
    IssueAccessTokenCommand,
)
from learn_fastapi.src.auth.application.use_cases import (
    CreateRefreshTokenUseCase,
    IssueAccessTokenUseCase,
)
from learn_fastapi.src.auth.domain.entities import PersistedRefreshToken
from learn_fastapi.src.shared.domain.value_object import UserId


class FixedClock:
    """Clock fake with a deterministic value for application tests."""

    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeAccessTokenIssuer:
    """Token issuer fake that exposes its inputs in the token value."""

    def issue(self, user_id: UserId, expires_at: datetime) -> str:
        return f"access:{user_id}:{expires_at.isoformat()}"


class FakeRefreshTokenGenerator:
    """Refresh token generator fake with a stable raw token."""

    def generate(self) -> str:
        return "raw-refresh-token"


class FakeRefreshTokenHasher:
    """Refresh token hasher fake that makes assertions readable."""

    def hash(self, token: str) -> str:
        return f"hashed:{token}"


class FakeAuthRepository:
    """In-memory auth repository for token creation tests."""

    def __init__(self) -> None:
        self.created_tokens: list[tuple[UserId, str, datetime]] = []

    async def get_refresh_token(self, owner_id: UserId) -> PersistedRefreshToken | None:
        return None

    async def create_refresh_token(
        self,
        user_id: UserId,
        token_hash: str,
        expires_at: datetime,
    ) -> PersistedRefreshToken:
        self.created_tokens.append((user_id, token_hash, expires_at))
        return PersistedRefreshToken(
            id=uuid4(),
            owner_id=user_id,
            token_hash=token_hash,
        )

    async def revoke_refresh_tokens(self, owner_id: UserId) -> None:
        return None

    async def revoke_refresh_token(
        self,
        token: PersistedRefreshToken,
        token_raw: str,
    ) -> None:
        return None


async def test_issue_access_token_uses_clock_and_configured_lifetime() -> None:
    user_id = uuid4()
    now = datetime(2026, 7, 25, 12, 0, tzinfo=UTC)
    use_case = IssueAccessTokenUseCase(
        token_issuer=FakeAccessTokenIssuer(),
        clock=FixedClock(now),
        expires_in=timedelta(minutes=30),
    )

    result = await use_case.execute(IssueAccessTokenCommand(user_id))

    assert result.expires_at == now + timedelta(minutes=30)
    assert result.expires_in == 1800
    assert result.value == f"access:{user_id}:{result.expires_at.isoformat()}"


async def test_create_refresh_token_hashes_and_persists_generated_token() -> None:
    user_id = uuid4()
    now = datetime(2026, 7, 25, 12, 0, tzinfo=UTC)
    repository = FakeAuthRepository()
    use_case = CreateRefreshTokenUseCase(
        auth_repository=repository,
        token_generator=FakeRefreshTokenGenerator(),
        token_hasher=FakeRefreshTokenHasher(),
        clock=FixedClock(now),
        expires_in=timedelta(days=7),
    )

    result = await use_case.execute(CreateRefreshTokenCommand(user_id))

    assert result.value == "raw-refresh-token"
    assert result.expires_at == now + timedelta(days=7)
    assert result.expires_in == 604800
    assert repository.created_tokens == [
        (user_id, "hashed:raw-refresh-token", now + timedelta(days=7))
    ]
