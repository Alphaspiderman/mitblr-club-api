from datetime import datetime, timedelta
from typing import List, Literal, Optional

import jwt
from jwt import InvalidTokenError
from sanic import Request, Sanic


async def check_request_for_authorization_status(
    request: Request,
    require_any: List[
        Optional[
            Literal[
                "signup",
                "student",
                "faculty",
                "external",
                "team",
                "admin",
                "automation",
            ]
        ]
    ],
) -> bool:
    """Checks if the given request is containing a basic auth token"""
    if not request.token:
        return False

    options = {
        "verify_signature": True,
        "require": ["exp", "nbf", "iat", "iss", "state"],
        "verify_iss": True,
        "verify_exp": True,
        "verify_iat": True,
        "verify_nbf": True,
    }

    try:
        data = jwt.decode(
            request.token,
            key=request.app.config["PUB_KEY"],
            algorithms="RS256",
            options=options,
        )
    except InvalidTokenError:
        return False

    # Check if we require a specific scope
    if require_any:
        for scope in require_any:
            if data["state"] == scope:
                return True
        return False
    else:
        return True


async def generate_jwt(
    app: Sanic,
    data: dict,
    validity: int,
    target: Literal[
        "signup", "student", "faculty", "external", "team", "admin", "automation"
    ],
) -> str:
    """Generates JWT with given data"""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=validity)

    try:
        # Attempt to get Host from config
        host = app.config["HOST"]
    except KeyError:
        # Unable to get Host from config, Quit app due to required field
        app.stop()

    iss = f"MITBLR_CLUB_API_{host}"
    data.update(
        {"exp": expire, "iat": now, "nbf": now, "iss": iss, "state": target.lower()}
    )
    return jwt.encode(data, app.config["PRIV_KEY"], algorithm="RS256")
