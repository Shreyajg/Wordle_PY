import random

from app.controller.schemas import CurrentGameResponse, GameResponse
from app.exception.game_exception import GameException
from app.model.enums import LetterResult, Status
from app.model.game import Game
from app.repository.game_repository import GameRepository
from app.repository.word_repository import WordRepository
from app.service.dates import day_bounds, now_local

MAX_GAMES_PER_DAY = 3
MAX_GUESSES = 5
WORD_LENGTH = 5


def calculate_result(target: str, guess: str) -> list[LetterResult]:
    result: list[LetterResult | None] = [None] * WORD_LENGTH
    used = [False] * WORD_LENGTH

    # First pass: GREEN
    for i in range(WORD_LENGTH):
        if guess[i] == target[i]:
            result[i] = LetterResult.GREEN
            used[i] = True

    # Second pass: ORANGE / GREY
    for i in range(WORD_LENGTH):
        if result[i] is not None:
            continue
        for j in range(WORD_LENGTH):
            if not used[j] and guess[i] == target[j]:
                result[i] = LetterResult.ORANGE
                used[j] = True
                break
        if result[i] is None:
            result[i] = LetterResult.GREY

    return result


class GameService:

    def __init__(self, game_repository: GameRepository, word_repository: WordRepository):
        self.game_repository = game_repository
        self.word_repository = word_repository

    async def start_game(self, player_id: str) -> Game:
        start_of_day, end_of_day = day_bounds(now_local().date())
        active_game = await self.game_repository.find_by_player_id_and_status(
            player_id, Status.IN_PROGRESS
        )
        if active_game is not None:
            return active_game

        games_today = await self.game_repository.find_by_player_id_and_created_at_between(
            player_id, start_of_day, end_of_day
        )
        if len(games_today) >= MAX_GAMES_PER_DAY:
            raise GameException("Limits exceeded ! try again tomorrow!")

        words = await self.word_repository.find_all()
        if not words:
            raise GameException("No words in the database")
        word = random.choice(words)
        game = Game(player_id, word.word, [], Status.IN_PROGRESS, now_local())
        return await self.game_repository.save(game)

    async def make_guess_word(self, player_id: str, guess: str | None) -> GameResponse:
        curr_game = await self.game_repository.find_by_player_id_and_status(
            player_id, Status.IN_PROGRESS
        )
        if curr_game is None:
            raise GameException("Please start a game")

        # validate guess
        guess = (guess or "").strip().upper()
        if len(guess) != WORD_LENGTH:
            raise GameException("Word length should be equal to 5")
        if await self.word_repository.find_by_word(guess) is None:
            raise GameException("Word is not in the word list")
        if any(c < "A" or c > "Z" for c in guess):
            raise GameException("please enter a valid guess")

        target_word = curr_game.target_word.strip().upper()
        result = calculate_result(target_word, guess)
        curr_game.guesses.append(guess)

        if all(r == LetterResult.GREEN for r in result):
            curr_game.status = Status.WON
        elif len(curr_game.guesses) == MAX_GUESSES:
            curr_game.status = Status.LOST

        await self.game_repository.save(curr_game)
        return GameResponse(results=result, status=curr_game.status)

    async def get_current_game(self, player_id: str) -> CurrentGameResponse:
        active_game = await self.game_repository.find_by_player_id_and_status(
            player_id, Status.IN_PROGRESS
        )
        if active_game is None:
            return CurrentGameResponse(guesses=[], results=[], status=Status.IN_PROGRESS)
        return self.get_game_response(active_game)

    def get_game_response(self, game: Game) -> CurrentGameResponse:
        results = [calculate_result(game.target_word, g) for g in game.guesses]
        return CurrentGameResponse(guesses=game.guesses, results=results, status=game.status)
