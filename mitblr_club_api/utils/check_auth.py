import jwt
from jwt import InvalidTokenError
from sanic import Request


async def check_request_for_authorization_status(request: Request) -> bool:
    """Checks if the given request is containing a basic auth token"""
    if not request.token:
        return False

    try:
        jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")
    except InvalidTokenError:
        return False

    return True
