from enum import Enum

from bson import ObjectId
from pydantic import BaseModel


class Course(Enum):
    CSE_CORE = "CSE_CORE"
    CSE_AI = "CSE_AI"
    CSE_CYBER = "CSE_CYBER"
    IT = "IT"
    ECE = "ECE"


class MessProvider(Enum):
    BLUE_DOVE = "BlueDove"
    CHEFS_TOUCH = "ChefsTouch"
    GROUP_A = "GroupA"
    GROUP_B = "GroupB"


class Student(BaseModel):
    _id: ObjectId
    academic: dict[str, Course | int]
    application_number: int
    clubs: list[ObjectId]
    email: str
    events: dict[str, ObjectId]
    institution: str
    mess_provider: MessProvider
    name: str
    phone_number: str
    registration_number: int

    class Config:
        arbitrary_types_allowed = True


class Student_Create(BaseModel):
    academic: dict[str, Course | int]
    application_number: int
    clubs: list[str]
    email: str
    institution: str
    mess_provider: MessProvider
    name: str
    phone_number: str
    registration_number: int

    class Config:
        arbitrary_types_allowed = True
