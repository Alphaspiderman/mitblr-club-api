from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.user import User


class Students(HTTPMethodView):
    @authorized_incls
    async def get(self, request: Request, uuid: int):
        """Check if Student Exists"""
        collection = request.app.ctx.db["students"]
        doc = await collection.find_one(
            {"$or": [{"application_number": uuid}, {"registration_number": uuid}]}
        )

        if doc is None:
            d = {"exists": "False"}
        else:
            d = {"exists": "True", "registration_number": doc["registration_number"]}

        return json(d)

    @authorized_incls
    @validate(json=User)
    async def post(self, request: Request, uuid, body: User):
        """Create Student in DB"""

        collection = request.app.ctx.db["students"]
        doc = await collection.find_one(
            {"$or": [{"application_number": uuid}, {"registration_number": uuid}]}
        )

        if doc is None:
            user = dict()
            user["application_number"] = body.application_number
            user["registration_number"] = body.registration_number
            user["email"] = body.email
            user["institution"] = body.institution
            user["phone_number"] = body.phone_no
            user["stay"] = {"mess": body.mess}.update(body.hostel)
            user["academic"] = body.academic
            user["name"] = body.name
            result = await collection.insert_one(user)
            d = {"Insert": "True", "ObjectId": str(result.inserted_id)}
            return json(d)

        else:
            d = {"Error Code": "409", "Message": "Conflict - Object already exists"}
            return json(d, status=409)

    # TODO - Scope Check
    @authorized_incls
    async def patch(self, request: Request, uuid: str):
        ...


appserver.add_route(Students.as_view(), "/students/<uuid:strorempty>")