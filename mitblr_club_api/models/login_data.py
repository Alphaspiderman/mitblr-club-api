from pydantic import BaseModel
import typing


class Login_Data(BaseModel):
    auth_type: typing.Literal["USER", "AUTOMATION"]
    identifier: str
    secret: str
