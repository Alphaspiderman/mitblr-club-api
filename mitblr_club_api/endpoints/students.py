from sanic.views import HTTPMethodView
from sanic.response import json, BaseHTTPResponse
from sanic.request import Request
from sanic.log import logger

from ..app import appserver


class Students(HTTPMethodView):
    # TODO - Add view wide Decorators for authentication before we give/alter personal info

    async def get(self, request: Request, uuid: int):
        """Check if Student Exists"""
        collection = request.app.ctx.db["students"]
        doc = await collection.find_one(
            {"$or": [{"application_number": uuid}, {"registeration_number": uuid}]}
        )

        if doc is None:
            d = {"exists": "False"}
        else:
            d = {"exists": "True", "registeration_number": doc["registeration_number"]}

        return json(d)

    # TODO - Data Validation
    async def post(request: Request, uuid: int):
        """Create Student in DB"""
        collection = request.app.ctx.db["students"]
        doc = await collection.find_one(
            {"$or": [{"application_number": id}, {"registeration_number": id}]}
        )

        if doc is None:
            # Can create
            d = {"Status": "Work in Progress"}
            return json(d)

        else:
            d = {"Error Code": "409", "Message": "Confict - Object already exists"}
            return json(d, status=409)

    # TODO - Scope Check
    async def patch(self, request: Request, id: int):
        ...


appserver.add_route(Students.as_view(), "/students/<uuid:int>")
