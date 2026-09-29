from fastapi import Depends, Request

from app.config.dependencies import get_jwt_service, get_user_repository
from app.exception.game_exception import ForbiddenException
from app.model.enums import Role
from app.model.user import User
from app.repository.user_repository import UserRepository
from app.service.jwt_service import JwtService

TOKEN_COOKIE = "token"


async def get_authenticated_user(
    request: Request,
    jwt_service: JwtService = Depends(get_jwt_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    token = request.cookies.get(TOKEN_COOKIE)
    if not token or not token.strip():
        raise ForbiddenException()

    username = jwt_service.extract_username(token)
    if username is None or not jwt_service.validate_token(token, username):
        raise ForbiddenException()

    user = await user_repository.find_by_username(username)
    if user is None:
        raise ForbiddenException()
    return user


def require_roles(*roles: Role):

    async def check(user: User = Depends(get_authenticated_user)) -> User:
        if user.role not in roles:
            raise ForbiddenException()
        return user

    return check
