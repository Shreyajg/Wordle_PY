from app.model.word import Word
from app.repository.word_repository import WordRepository

WORDS = [
    "APPLE", "BRAVE", "CLOUD", "DREAM", "EARTH",
    "FLAME", "GRAPE", "HOUSE", "LIGHT", "MUSIC",
    "NIGHT", "OCEAN", "PIANO", "QUEEN", "RIVER",
    "SMILE", "STONE", "TABLE", "TRAIN", "WORLD",
]


async def seed_words(word_repository: WordRepository) -> None:
    if await word_repository.count() == 0:
        for word in WORDS:
            await word_repository.save(Word(word))
