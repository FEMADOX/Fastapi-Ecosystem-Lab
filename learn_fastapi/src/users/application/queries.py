from dataclasses import dataclass

from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(slots=True, frozen=True)
class GetUserByIdQuery:
    user_id: UserId


@dataclass(slots=True, frozen=True)
class GetUserByEmailQuery:
    user_email: str
