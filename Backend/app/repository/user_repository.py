from typing import Optional

from app.model import user as user_model
from app.model.user import User
from app.repository._ids import to_object_id


class UserRepository:

    def __init__(self, db):
        self.collection = db[user_model.COLLECTION]

    async def find_by_username(self, username: str) -> Optional[User]:
        doc = await self.collection.find_one({"username": username})
        return User.from_document(doc) if doc else None

    async def save(self, user: User) -> User:
        if user.id is None:
            result = await self.collection.insert_one(user.to_document())
            user.id = str(result.inserted_id)
        else:
            await self.collection.replace_one(
                {"_id": to_object_id(user.id)}, user.to_document(), upsert=True
            )
        return user
