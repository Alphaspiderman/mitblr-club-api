from datetime import datetime

from pydantic import BaseModel


class EventRequest(BaseModel):
    date: datetime
    location: str
    name: str

    class Config:
        arbitrary_types_allowed = True
