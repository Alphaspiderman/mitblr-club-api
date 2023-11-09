from bson import ObjectId
from pydantic import BaseModel

from mitblr_club_api.models.enums.core_committee import CoreCommittee
from mitblr_club_api.models.enums.unit import Unit


class ClubCache(BaseModel):
    _id: ObjectId
    core_committee: dict[CoreCommittee, ObjectId]
    faculty_advisors: list[dict[str, str]]
    institution: str
    name: str
    operations: list[ObjectId]
    slug: str
    unit_type: Unit

    class Config:
        arbitrary_types_allowed = True
