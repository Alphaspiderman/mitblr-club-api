from typing import List, Literal, Optional
from sanic.response import json

from mitblr_club_api.utils import check_request_for_authorization_status


def authorized(
    require: Optional[
        List[
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
    ] = None
):
    if require is None:
        require = []

    def decorator(f):
        async def decorated_function(*args, **kwargs):
            # run some method that checks the request
            # for the client's authorization status

            is_authorized = await check_request_for_authorization_status(
                args[1], require_any=require
            )

            if is_authorized:
                # the user is authorized.
                # run the handler method and return the response
                response = await f(*args, **kwargs)
                return response
            else:
                # the user is not authorized.
                return json({"status": "not_authorized"}, 403)

        return decorated_function

    return decorator
