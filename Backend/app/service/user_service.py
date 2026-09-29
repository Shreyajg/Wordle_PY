from typing import Optional

from app.config.password_encoder import PasswordEncoder
from app.exception.game_exception import GameException
from app.model.enums import Role
from app.model.user import User
from app.repository.user_repository import UserRepository


def _has_upper_and_lower(value: str) -> tuple[bool, bool]:
    upper = any(c.isalpha() and c.isupper() for c in value)
    lower = any(c.isalpha() and c.islower() for c in value)
    return upper, lower


class UserService:

    def __init__(self, user_repository: UserRepository, password_encoder: PasswordEncoder):
        self.user_repository = user_repository
        self.password_encoder = password_encoder

    async def find_by_username(self, username: str) -> User:
        user = await self.user_repository.find_by_username(username)
        if user is None:
            raise GameException("User not found")
        return user

    async def register(
        self, username: Optional[str], password: Optional[str], confirm_password: Optional[str]
    ) -> User:
        username = username or ""
        password = password or ""

        if len(username) < 5:
            raise GameException("username should have a minimum of 5 characters")
        upper, lower = _has_upper_and_lower(username)
        if not upper or not lower:
            raise GameException("Username must contain atleast one upper and lower letters")

        if await self.user_repository.find_by_username(username) is not None:
            raise GameException("Username already exists try logging in")

        if len(password) < 5:
            raise GameException("Password should have a minimum length of 5")
        upper, lower = _has_upper_and_lower(password)
        num = any(c.isdigit() for c in password)
        special = any(c in "$%*" for c in password)
        if not upper or not lower or not num or not special:
            raise GameException(
                "Password should have atleast one lower case letter atleast one upper case "
                "letter atleast one number and atleast on of the ($,% or *)"
            )
        if password != confirm_password:
            raise GameException("Passwords dont match")

        password_hash = self.password_encoder.encode(password)
        return await self.user_repository.save(User(username, password_hash, Role.PLAYER))

    async def login(self, username: Optional[str], password: Optional[str]) -> User:
        user = await self.user_repository.find_by_username(username)
        if user is None:
            raise GameException("User not found please register")
        if self.password_encoder.matches(password, user.password_hash):
            return user
        raise GameException("Username or password is incorrect")
