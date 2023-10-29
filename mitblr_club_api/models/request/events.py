from datetime import datetime

from pydantic import BaseModel


class Event_Request(BaseModel):
    date: datetime
    location: str
    name: str

    class Config:
        arbitrary_types_allowed = True
