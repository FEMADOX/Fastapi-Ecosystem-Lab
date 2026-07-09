from learn_fastapi.src.auth.domain.entities import RefreshToken as RefreshTokenDomain
from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM


def refresh_token_from_orm(orm_token: RefreshTokenORM) -> RefreshTokenDomain:
    """Convert an ORM refresh token to a domain refresh token.

    Args:
        orm_token (RefreshTokenORM): The ORM refresh token to convert.

    Returns:
        RefreshTokenDomain: The corresponding domain refresh token.

    """
    return RefreshTokenDomain(
        id=orm_token.id,
        owner_id=orm_token.user_id,
        token_hash=orm_token.token_hash,
        created_at=orm_token.created_at,
        expires_at=orm_token.expires_at,
        revoked_at=orm_token.revoked_at,
    )


# def refresh_token_domain_to_schema(domain_token: RefreshTokenDomain) -> RefreshToken:
#     """Convert a domain refresh token to a schema refresh token.

#     Args:
#         domain_token (RefreshTokenDomain): The domain refresh token to convert.

#     Returns:
#         ItemSchema: The corresponding schema item.

#     """
#     return ItemSchema(
#         id=domain_item.id,
#         user_id=domain_item.owner_id,
#         name=domain_item.name,
#         description=domain_item.description,
#         price=domain_item.price,
#         tax=domain_item.tax,
#         image_url=domain_item.image_url,
#     )
