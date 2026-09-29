from typing import Optional

from app.model import word as word_model
from app.model.word import Word


class WordRepository:

    def __init__(self, db):
        self.collection = db[word_model.COLLECTION]

    async def find_by_word(self, word: str) -> Optional[Word]:
        doc = await self.collection.find_one({"word": word})
        return Word.from_document(doc) if doc else None

    async def find_all(self) -> list[Word]:
        docs = await self.collection.find({}).to_list(None)
        return [Word.from_document(d) for d in docs]

    async def count(self) -> int:
        return await self.collection.count_documents({})

    async def save(self, word: Word) -> Word:
        result = await self.collection.insert_one(word.to_document())
        word.id = str(result.inserted_id)
        return word
