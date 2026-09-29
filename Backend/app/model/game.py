from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.model.enums import Status

COLLECTION = "games"
CLASS_NAME = "com.example.guessgame.model.Game"


@dataclass
class Game:
    player_id: str
    target_word: str
    guesses: list[str] = field(default_factory=list)
    status: Status = Status.IN_PROGRESS
    created_at: Optional[datetime] = None
    id: Optional[str] = None

    def to_document(self) -> dict[str, Any]:
        return {
            "playerId": self.player_id,
            "targetWord": self.target_word,
            "guesses": self.guesses,
            "status": self.status.value,
            "createdAt": self.created_at,
            "_class": CLASS_NAME,
        }

    @classmethod
    def from_document(cls, doc: dict[str, Any]) -> "Game":
        return cls(
            id=str(doc["_id"]),
            player_id=doc.get("playerId"),
            target_word=doc.get("targetWord"),
            guesses=list(doc.get("guesses") or []),
            status=Status(doc.get("status")),
            created_at=doc.get("createdAt"),
        )
