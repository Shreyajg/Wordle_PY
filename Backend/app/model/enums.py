from enum import Enum


class Role(str, Enum):
    PLAYER = "PLAYER"
    ADMIN = "ADMIN"


class Status(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WON = "WON"
    LOST = "LOST"


class LetterResult(str, Enum):
    GREEN = "GREEN"
    ORANGE = "ORANGE"
    GREY = "GREY"
