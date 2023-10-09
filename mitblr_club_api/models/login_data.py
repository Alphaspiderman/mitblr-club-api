from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class LoginData:
    auth_type: Literal["USER", "AUTOMATION"]
    identifier: str
    secret: str
