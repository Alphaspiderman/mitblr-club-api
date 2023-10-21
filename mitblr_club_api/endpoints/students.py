from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from bson import ObjectId

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.students import Student_Create


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
    @validate(json=Student_Create)
    async def post(self, request: Request, body: Student_Create, uuid: str):
        """Create Student in DB"""

        collection = request.app.ctx.db["students"]
        doc = await collection.find_one({"application_number": body.application_number})


        if doc is None:
            student = dict()
            student["application_number"] = body.application_number
            student["email"] = body.email
            student["institution"] = body.institution
            student["academic"] = {
                "stream": body.academic["stream"].value,
                "year_pass": body.academic["year_pass"],
            }
            student["phone_number"] = body.phone_number
            student["registration_number"] = body.registration_number
            student["clubs"] = [ObjectId(oid=x) for x in body.clubs]
            student["name"] = body.name
            student["mess_provider"] = body.mess_provider.value

            result = await collection.insert_one(student)
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
