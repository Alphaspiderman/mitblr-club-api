import typing
from dataclasses import dataclass


@dataclass(slots=True)
class LoginData:
    auth_type: typing.Literal["USER", "AUTOMATION"]
    identifier: str
    secret: str
