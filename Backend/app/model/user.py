from dataclasses import dataclass
from typing import Any, Optional

from app.model.enums import Role

COLLECTION = "users"
CLASS_NAME = "com.example.guessgame.model.User"


@dataclass
class User:
    username: str
    password_hash: str
    role: Role
    id: Optional[str] = None

    def to_document(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "passwordHash": self.password_hash,
            "role": self.role.value,
            "_class": CLASS_NAME,
        }

    @classmethod
    def from_document(cls, doc: dict[str, Any]) -> "User":
        return cls(
            id=str(doc["_id"]),
            username=doc.get("username"),
            password_hash=doc.get("passwordHash"),
            role=Role(doc.get("role")),
        )
