from dataclasses import dataclass

from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(frozen=True, slots=True)
class RegisterNewUserCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    user_id: UserId
    new_email: str | None
    new_password: str | None


@dataclass(frozen=True, slots=True)
class DeleteUserCommand:
    user_id: UserId
