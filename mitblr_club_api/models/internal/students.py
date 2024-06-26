from bson import ObjectId
from pydantic import BaseModel

from mitblr_club_api.models.enums.course import Course
from mitblr_club_api.models.enums.mess_provider import MessProvider


class Student(BaseModel):
    _id: ObjectId
    academic: dict[str, Course | int]
    application_number: int
    clubs: list[ObjectId]
    email: str
    events: list
    institution: str
    mess_provider: MessProvider
    name: str
    phone_number: str
    registration_number: int

    class Config:
        arbitrary_types_allowed = True
