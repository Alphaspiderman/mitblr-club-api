from sanic.response import json

from ..utils.check_auth import check_request_for_authorization_status


def authorized(f):
    def decorator(*args, **kwargs):
        # @wraps(f)
        async def decorated_function(*args, **kwargs):
            # run some method that checks the request
            # for the client's authorization status
            is_authorized = await check_request_for_authorization_status(args[0])

            if is_authorized:
                # the user is authorized.
                # run the handler method and return the response
                response = await f(*args, **kwargs)
                return response
            else:
                # the user is not authorized.
                return json({"status": "not_authorized"}, 403)

        return decorated_function(*args, **kwargs)

    return decorator


def authorized_incls(f):
    def decorator(*args, **kwargs):
        # @wraps(f)
        async def decorated_function(*args, **kwargs):
            # run some method that checks the request
            # for the client's authorization status
            is_authorized = await check_request_for_authorization_status(args[1])

            if is_authorized:
                # the user is authorized.
                # run the handler method and return the response
                response = await f(*args, **kwargs)
                return response
            else:
                # the user is not authorized.
                return json({"status": "not_authorized"}, 403)

        return decorated_function(*args, **kwargs)

    return decorator
