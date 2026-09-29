from fastapi import APIRouter, Depends

from app.config.dependencies import get_game_service
from app.config.security_config import require_roles
from app.controller.schemas import CurrentGameResponse, GameResponse, GuessRequest
from app.model.enums import Role
from app.model.user import User
from app.service.game_service import GameService

router = APIRouter(prefix="/games")

player_or_admin = require_roles(Role.PLAYER, Role.ADMIN)


@router.post("/start", response_model=CurrentGameResponse)
async def start_game(
    user: User = Depends(player_or_admin),
    game_service: GameService = Depends(get_game_service),
):
    game = await game_service.start_game(user.id)
    return game_service.get_game_response(game)


@router.post("/guess", response_model=GameResponse)
async def make_guess_word(
    request: GuessRequest,
    user: User = Depends(player_or_admin),
    game_service: GameService = Depends(get_game_service),
):
    return await game_service.make_guess_word(user.id, request.guess)


@router.get("/current", response_model=CurrentGameResponse)
async def get_current_game(
    user: User = Depends(player_or_admin),
    game_service: GameService = Depends(get_game_service),
):
    return await game_service.get_current_game(user.id)
