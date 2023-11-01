from typing import Literal

from pydantic import BaseModel


class Login(BaseModel):
    auth_type: Literal["USER", "AUTOMATION"]
    identifier: str
    secret: str
