"""
ClubTeam document model.
"""
from pydantic import BaseModel


class ClubTeam(BaseModel):
    """
    ClubTeam document model.
    """

    _id: str
    api_access: bool
    auth: str
    club: str
    permissions: dict[str, bool]
    position: dict[str, str]
    student_id: str
