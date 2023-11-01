from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel

from mitblr_club_api.models.enums.clubs import Club


class Event(BaseModel):
    _id: ObjectId
    club: Club
    date: datetime
    location: str
    name: str
    participants: dict[str, list[ObjectId]]
    slug: str

    class Config:
        arbitrary_types_allowed = True
