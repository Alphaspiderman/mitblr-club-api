from sanic import Request
import jwt


async def check_request_for_authorization_status(request: Request):
    """Checks if the given request is containing a basic auth token"""
    if not request.token:
        return False

    try:
        jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True
