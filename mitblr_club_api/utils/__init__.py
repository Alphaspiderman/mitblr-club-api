from datetime import datetime, timedelta

import jwt
from jwt import InvalidTokenError
from sanic import Request, Sanic


async def check_request_for_authorization_status(request: Request) -> bool:
    """Checks if the given request is containing a basic auth token"""
    if not request.token:
        return False

    try:
        jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")
    except InvalidTokenError:
        return False

    return True


async def generate_jwt(app: Sanic, data: dict, validity: int) -> str:
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
    data.update({"exp": expire, "iat": now, "nbf": now, "iss": iss})
    return jwt.encode(data, app.config["PRIV_KEY"], algorithm="RS256")
