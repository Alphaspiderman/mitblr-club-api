from pydantic import BaseModel


class MsAuth(BaseModel):
    """Query parameters for the MS-Entra authentication endpoint."""

    user_id: str
    service: str
