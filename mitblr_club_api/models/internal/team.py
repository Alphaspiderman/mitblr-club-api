"""
ClubTeam document model.
"""
from bson import ObjectId
from pydantic import BaseModel


class Team(BaseModel):
    """
    ClubTeam document model.
    """

    _id: ObjectId
    api_access: bool
    auth: ObjectId
    club: str
    permissions: dict[str, bool]
    position: dict[str, str]
    student_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
