from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.model.enums import LetterResult, Status


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AuthRequest(CamelModel):
    username: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None


class AuthResponse(CamelModel):
    token: Optional[str] = None
    username: str
    role: str


class GuessRequest(CamelModel):
    guess: Optional[str] = None


class GameResponse(CamelModel):
    results: list[LetterResult]
    status: Status


class CurrentGameResponse(CamelModel):
    guesses: list[str]
    results: list[list[LetterResult]]
    status: Status


class AdminResponse(CamelModel):
    no_of_users: int
    no_of_users_today: int
    no_of_correct_guesses: int


class AdminUserResponse(CamelModel):
    date: date
    no_of_words_tried: int
    no_of_correct_guesses: int
