from datetime import datetime, timedelta

import jwt
from sanic import Sanic


async def generate_jwt(app: Sanic, data: dict, validity: int):
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
