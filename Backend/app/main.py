from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI

from app.config.cors_config import add_cors
from app.config.data_seeder import seed_words
from app.config.database import create_client, get_database
from app.config.settings import Settings, get_settings
from app.controller import admin_controller, auth_controller, game_controller
from app.exception.global_exception_handler import register_exception_handlers
from app.repository.word_repository import WordRepository
from app.service.jwt_service import JwtService


def create_app(settings: Optional[Settings] = None, db=None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        client = None
        if db is None:
            client = create_client(settings)
            app.state.db = get_database(client, settings)
        else:
            app.state.db = db
        app.state.jwt_service = JwtService(settings.jwt_secret)
        await seed_words(WordRepository(app.state.db))
        yield
        if client is not None:
            await client.close()

    app = FastAPI(title="guess-game", lifespan=lifespan)
    add_cors(app, settings.cors_origins)
    register_exception_handlers(app)
    app.include_router(auth_controller.router)
    app.include_router(game_controller.router)
    app.include_router(admin_controller.router)
    return app


if __name__ == "__main__":
    uvicorn.run("app.main:create_app", factory=True, host="0.0.0.0", port=get_settings().port)
