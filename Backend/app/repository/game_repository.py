from datetime import datetime
from typing import Optional

from app.model import game as game_model
from app.model.enums import Status
from app.model.game import Game
from app.repository._ids import to_object_id


def _between(start: datetime, end: datetime) -> dict:
    return {"$gte": start, "$lte": end}


class GameRepository:

    def __init__(self, db):
        self.collection = db[game_model.COLLECTION]

    async def _find(self, query: dict) -> list[Game]:
        docs = await self.collection.find(query).to_list(None)
        return [Game.from_document(d) for d in docs]

    async def find_by_player_id_and_created_at_between(
        self, player_id: str, start: datetime, end: datetime
    ) -> list[Game]:
        return await self._find({"playerId": player_id, "createdAt": _between(start, end)})

    async def find_by_player_id_and_status(
        self, player_id: str, status: Status
    ) -> Optional[Game]:
        doc = await self.collection.find_one({"playerId": player_id, "status": status.value})
        return Game.from_document(doc) if doc else None

    async def find_by_status_and_created_at_between(
        self, status: Status, start: datetime, end: datetime
    ) -> list[Game]:
        return await self._find({"status": status.value, "createdAt": _between(start, end)})

    async def find_by_player_id_and_status_and_created_at_between(
        self, player_id: str, status: Status, start: datetime, end: datetime
    ) -> list[Game]:
        return await self._find(
            {"playerId": player_id, "status": status.value, "createdAt": _between(start, end)}
        )

    async def find_unique_player_ids_by_created_at_between(
        self, start: datetime, end: datetime
    ) -> list[str]:
        pipeline = [
            {"$match": {"createdAt": {"$gte": start, "$lt": end}}},
            {"$group": {"_id": "$playerId"}},
            {"$project": {"_id": 0, "playerId": "$_id"}},
        ]
        cursor = await self.collection.aggregate(pipeline)
        docs = await cursor.to_list(None)
        return [d["playerId"] for d in docs]

    async def save(self, game: Game) -> Game:
        if game.id is None:
            result = await self.collection.insert_one(game.to_document())
            game.id = str(result.inserted_id)
        else:
            await self.collection.replace_one(
                {"_id": to_object_id(game.id)}, game.to_document(), upsert=True
            )
        return game
