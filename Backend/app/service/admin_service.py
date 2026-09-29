from datetime import date

from app.controller.schemas import AdminResponse, AdminUserResponse
from app.model.enums import Status
from app.repository.game_repository import GameRepository
from app.service.dates import day_bounds


class AdminService:

    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    async def get_daily_report(self, day: date) -> AdminResponse:
        start_of_day, end_of_day = day_bounds(day)
        no_of_users = len(
            await self.game_repository.find_unique_player_ids_by_created_at_between(
                start_of_day, end_of_day
            )
        )
        no_of_correct_guesses = len(
            await self.game_repository.find_by_status_and_created_at_between(
                Status.WON, start_of_day, end_of_day
            )
        )
        return AdminResponse(no_of_users=no_of_users, no_of_users_today=no_of_users,no_of_correct_guesses=no_of_correct_guesses)

    async def get_user_report(self, player_id: str, day: date) -> AdminUserResponse:
        start_of_day, end_of_day = day_bounds(day)
        no_of_games = len(
            await self.game_repository.find_by_player_id_and_created_at_between(
                player_id, start_of_day, end_of_day
            )
        )
        no_of_games_won = len(
            await self.game_repository.find_by_player_id_and_status_and_created_at_between(
                player_id, Status.WON, start_of_day, end_of_day
            )
        )
        return AdminUserResponse(
            date=day, no_of_words_tried=no_of_games, no_of_correct_guesses=no_of_games_won
        )
