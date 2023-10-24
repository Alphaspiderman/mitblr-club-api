from enum import Enum

from bson import ObjectId
from pydantic import BaseModel


class CoreCommittee(Enum):
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    TREASURER = "treasurer"
    EXECUTIVE_SECRETARY = "executive_secretary"
    GENERAL_SECRETARY = "general_secretary"
    OPERATIONS_LEAD = "operations_lead"


class Unit(Enum):
    CHAPTER = "chapter"
    CLUB = "club"
    SOCIETY = "society"


class Club(BaseModel):
    _id: ObjectId
    core_committee: dict[CoreCommittee, ObjectId]
    events: dict[int, list[ObjectId]]
    faculty_advisors: list[dict[str, str]]
    institution: str
    name: str
    operations: list[ObjectId]
    slug: str
    unit_type: Unit

    class Config:
        arbitrary_types_allowed = True


class Club_Create(BaseModel):
    faculty_advisors: list[dict[str, str]]
    institution: str
    name: str
    slug: str
    unit_type: Unit

    class Config:
        arbitrary_types_allowed = True
