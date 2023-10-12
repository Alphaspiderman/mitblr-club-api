from datetime import datetime
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel


class Club(Enum):
    CODEX = "codex"


class Event(BaseModel):
    _id: ObjectId
    club: Club
    date: datetime
    location: str
    name: str
    participants: dict[str, list[ObjectId]]
    slug: str
