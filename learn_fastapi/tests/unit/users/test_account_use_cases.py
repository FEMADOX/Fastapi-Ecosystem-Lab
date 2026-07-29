from dataclasses import replace
from uuid import uuid4

import pytest

from learn_fastapi.src.shared.application.dto import (
    AuthenticatedAccount,
    CurrentActor,
)
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.application.commands import UpdateUserCommand
from learn_fastapi.src.users.application.queries import GetAccountQuery
from learn_fastapi.src.users.application.use_cases import (
    GetAccountUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
)
from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.domain.errors import (
    IncorrectPasswordError,
    OnlyOwnerIsAuthorizedError,
)
from learn_fastapi.src.users.domain.value_objects import PasswordHash


class FakePasswordHasher:
    def hash(self, password: str) -> PasswordHash:
        return PasswordHash(f"hashed:{password}")

    def verify(self, password: str, password_hash: PasswordHash) -> bool:
        return password_hash == self.hash(password)


class FakeUsersRepository:
    def __init__(self, *users: PersistedUser) -> None:
        self.users = {user.id: user for user in users}
        self.updated_user_ids: list[UserId] = []

    async def get_user_by_id(self, user_id: UserId) -> PersistedUser | None:
        return self.users.get(user_id)

    async def get_user_by_email(self, user_email: str) -> PersistedUser | None:
        return next(
            (user for user in self.users.values() if user.email == user_email),
            None,
        )

    async def get_user_by_refresh_token(
        self, refresh_token: str
    ) -> PersistedUser | None:
        return None

    async def create_user(self, email: str, password_hash: str) -> PersistedUser:
        raise NotImplementedError

    async def update_user(
        self,
        user_id: UserId,
        new_email: str | None,
        new_password_hash: str | None,
    ) -> PersistedUser:
        user = self.users[user_id]
        updated = replace(
            user,
            email=new_email or user.email,
            password_hash=(
                PasswordHash(new_password_hash)
                if new_password_hash
                else user.password_hash
            ),
        )
        self.users[user_id] = updated
        self.updated_user_ids.append(user_id)
        return updated

    async def delete_user(self, user_id: UserId) -> bool:
        return self.users.pop(user_id, None) is not None


class FakeUsersEventPublisher:
    def __init__(self) -> None:
        self.updated_user_ids: list[UserId] = []

    async def account_updated(
        self, user: PersistedUser, changed_fields: list[str]
    ) -> None:
        self.updated_user_ids.append(user.id)

    async def account_deleted(self, user: PersistedUser) -> None:
        return None


def make_user(*, is_superuser: bool = False) -> PersistedUser:
    return PersistedUser(
        id=uuid4(),
        items_ids=[],
        refresh_tokens_ids=[],
        email=f"{uuid4()}@example.com",
        password_hash=PasswordHash("hashed:current-password"),
        is_active=True,
        is_superuser=is_superuser,
    )


def authenticated_account(user: PersistedUser) -> AuthenticatedAccount:
    return AuthenticatedAccount(
        id=user.id,
        email=user.email,
        password_hash=user.password_hash,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )


async def test_get_account_rejects_non_owner() -> None:
    owner = make_user()
    other_user = make_user()
    repository = FakeUsersRepository(owner)
    use_case = GetAccountUseCase(GetUserByIdUseCase(repository))

    with pytest.raises(OnlyOwnerIsAuthorizedError):
        await use_case.execute(
            GetAccountQuery(
                user_id=owner.id,
                actor=CurrentActor(other_user.id, False),
            )
        )


async def test_update_account_rejects_incorrect_password_before_persistence() -> None:
    user = make_user()
    repository = FakeUsersRepository(user)
    use_case = UpdateUserUseCase(
        repository,
        FakePasswordHasher(),
        FakeUsersEventPublisher(),
    )

    with pytest.raises(IncorrectPasswordError):
        await use_case.execute(
            UpdateUserCommand(
                user_id=user.id,
                actor=authenticated_account(user),
                current_password="wrong-password",
                new_email="updated@example.com",
                new_password=None,
            )
        )

    assert repository.updated_user_ids == []


async def test_superuser_updates_requested_account() -> None:
    admin = make_user(is_superuser=True)
    target = make_user()
    repository = FakeUsersRepository(admin, target)
    events = FakeUsersEventPublisher()
    use_case = UpdateUserUseCase(repository, FakePasswordHasher(), events)

    updated, changed_fields = await use_case.execute(
        UpdateUserCommand(
            user_id=target.id,
            actor=authenticated_account(admin),
            current_password="current-password",
            new_email="target-updated@example.com",
            new_password=None,
        )
    )

    assert updated.id == target.id
    assert updated.email == "target-updated@example.com"
    assert repository.updated_user_ids == [target.id]
    assert events.updated_user_ids == [target.id]
    assert changed_fields == ["email"]
