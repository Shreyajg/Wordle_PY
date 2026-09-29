from pymongo import AsyncMongoClient

from app.config.settings import Settings


def create_client(settings: Settings) -> AsyncMongoClient:
    return AsyncMongoClient(settings.mongodb_uri)


def get_database(client: AsyncMongoClient, settings: Settings):
    return client.get_default_database(default=settings.mongodb_database)
