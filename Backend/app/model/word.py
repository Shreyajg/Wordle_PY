from dataclasses import dataclass
from typing import Any, Optional

COLLECTION = "words"
CLASS_NAME = "com.example.guessgame.model.Word"


@dataclass
class Word:
    word: str
    id: Optional[str] = None

    def to_document(self) -> dict[str, Any]:
        return {"word": self.word, "_class": CLASS_NAME}

    @classmethod
    def from_document(cls, doc: dict[str, Any]) -> "Word":
        return cls(id=str(doc["_id"]), word=doc.get("word"))
