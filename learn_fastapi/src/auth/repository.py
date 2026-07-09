from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, select, update

from learn_fastapi.src.auth.utils import verify_refresh_token
from learn_fastapi.src.users.models import User
from learn_fastapi.src.utils.repository import BaseRepository, bool_to_column

from .models import RefreshToken


class AuthRepository(BaseRepository):
    """Repository class for auth-related ORM operations."""

    async def get_refresh_token(self, user_id: UUID) -> RefreshToken | None:
        """Get the active refresh token for a user, handling duplicates.

        If multiple active tokens exist for the same user, keeps only the
        most recently created one and revokes the others.

        Args:
            user_id: The user ID to search for.

        Returns:
            The active refresh token, or None if none exists.

        """
        refresh_tokens = RefreshToken.__table__.c
        statement: Select[tuple[RefreshToken]] = (
            select(RefreshToken)
            .where(refresh_tokens.user_id == user_id)
            .where(refresh_tokens.revoked_at.is_(None))
            .where(refresh_tokens.expires_at > datetime.now(tz=UTC))
            .order_by(refresh_tokens.created_at.desc())
        )
        result = await self.session.scalars(statement)
        tokens = result.all()

        if not tokens:
            return None

        # If there are multiple tokens, keep only the newest and revoke the rest
        if len(tokens) > 1:
            newest_token = tokens[0]
            # Revoke all tokens except the newest
            for old_token in tokens[1:]:
                old_token.revoked_at = datetime.now(tz=UTC)
                self.session.add(old_token)
            await self.session.commit()
            return newest_token

        return tokens[0]

    async def create_refresh_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a new refresh token.

        Args:
            user_id: Owner of the refresh token.
            token_hash: Hashed refresh token value.
            expires_at: Expiration timestamp.

        Returns:
            The newly created refresh token record.

        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def revoke_refresh_token(self, user_id: UUID) -> None:
        """Revoke a refresh token record.

        Args:
            user_id: Owner of the refresh token.

        """
        refresh_tokens = RefreshToken.__table__.c
        await self.session.execute(
            update(RefreshToken)
            .where(refresh_tokens.user_id == user_id)
            .where(refresh_tokens.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self.commit()

    async def get_user_from_refresh_token(self, refresh_token: str) -> User | None:
        """Get the user associated with a valid refresh token.

        Args:
            refresh_token: The raw refresh token string to validate and search for.

        Returns:
            The associated user if the token is valid, or None if invalid.

        """
        # Argon2 hashes are salted, so hashing again and comparing with SQL equality
        # cannot match the stored value; fetch active tokens and verify per row.
        statement: Select[tuple[RefreshToken, User]] = (
            select(RefreshToken, User)
            .join(User, bool_to_column(RefreshToken.user_id == User.id))
            .where(RefreshToken.__table__.c.revoked_at.is_(None))
            .where(bool_to_column(RefreshToken.expires_at > datetime.now(tz=UTC)))
        )
        result = await self.session.execute(statement)
        for token_record, user in result.all():
            if verify_refresh_token(refresh_token, token_record.token_hash):
                return user

        return None
