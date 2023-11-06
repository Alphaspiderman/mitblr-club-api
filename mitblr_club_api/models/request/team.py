from pydantic import BaseModel


class ClubTeamRequest(BaseModel):
    """
    ClubTeam document creation model.
    """

    application_number: str
    api_access: bool
    club: str
    permissions: dict[str, bool]
    position: dict[str, str]
