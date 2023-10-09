import typing

from pydantic import BaseModel


class Login_Data(BaseModel):
    auth_type: typing.Literal["USER", "AUTOMATION"]
    identifier: str
    secret: str
