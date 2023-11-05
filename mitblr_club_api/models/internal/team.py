"""
ClubTeam document model.
"""
from pydantic import BaseModel
from bson import ObjectId


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
