from pydantic import BaseModel

from mitblr_club_api.models.enums.unit import Unit


class Club_Create(BaseModel):
    faculty_advisors: list[dict[str, str]]
    institution: str
    name: str
    slug: str
    unit_type: Unit

    class Config:
        arbitrary_types_allowed = True
