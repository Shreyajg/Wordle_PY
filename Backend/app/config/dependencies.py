from fastapi import Depends, Request

from app.config.password_encoder import PasswordEncoder
from app.repository.game_repository import GameRepository
from app.repository.user_repository import UserRepository
from app.repository.word_repository import WordRepository
from app.service.admin_service import AdminService
from app.service.game_service import GameService
from app.service.jwt_service import JwtService
from app.service.user_service import UserService

_password_encoder = PasswordEncoder()


def get_db(request: Request):
    return request.app.state.db


def get_jwt_service(request: Request) -> JwtService:
    return request.app.state.jwt_service


def get_password_encoder() -> PasswordEncoder:
    return _password_encoder


def get_user_repository(db=Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_word_repository(db=Depends(get_db)) -> WordRepository:
    return WordRepository(db)


def get_game_repository(db=Depends(get_db)) -> GameRepository:
    return GameRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    password_encoder: PasswordEncoder = Depends(get_password_encoder),
) -> UserService:
    return UserService(user_repository, password_encoder)


def get_game_service(
    game_repository: GameRepository = Depends(get_game_repository),
    word_repository: WordRepository = Depends(get_word_repository),
) -> GameService:
    return GameService(game_repository, word_repository)


def get_admin_service(
    game_repository: GameRepository = Depends(get_game_repository),
) -> AdminService:
    return AdminService(game_repository)
