from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from app.exception.game_exception import ForbiddenException, GameException


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(GameException)
    async def handle_game_exception(request: Request, e: GameException):
        return PlainTextResponse(e.message, status_code=400)

    @app.exception_handler(ForbiddenException)
    async def handle_forbidden(request: Request, e: ForbiddenException):
        return Response(status_code=403)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, e: RequestValidationError):
        return PlainTextResponse("Bad Request", status_code=400)
