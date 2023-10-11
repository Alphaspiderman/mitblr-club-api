from pydantic import BaseModel


class User(BaseModel):
    application_number: int
    registration_number: int
    name: str
    email: str
    institution: str
    hostel: dict
    mess: dict
    academic: dict
    clubs: list
    phone_no: int
