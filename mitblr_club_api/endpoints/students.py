"""API endpoints for students."""

from bson import ObjectId
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.students import Student_Create


class Students(HTTPMethodView):
    """Endpoints regarding students."""

    @authorized_incls
    async def get(self, request: Request, uuid: int):
        """
        Check if a student with given UUID exists in the database.

        :param request: Sanic request.
        :type request: Request
        :param uuid: UUID, which can either be the student's application number, or their registration number.
        :type uuid: int

        :return: JSON with "exists" set to "False" if the student does not exist, else JSON with "exists"
                 set to "True", and the student's registration number.
        :rtype: JSONResponse
        """

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
        """
        Create a student in the database using Python models.

        :param request: Sanic request.
        :type request: Request
        :param body: Body that contains data as a `Student_Create` object.
        :type body: Student_Create
        :param uuid: UUID, which can either be the student's application number, or their registration number.
        :type uuid: int

        :return: JSON response with the student's Mongo ObjectId if the student was successfully added to
                 the database. JSON response with code 409 if the student with the same application number
                 already exists.
        :rtype:
        """

        collection = request.app.ctx.db["students"]
        doc = await collection.find_one({"application_number": body.application_number})

        # parse each item in student['clubs'] and convert it into mongo object id
        # for i in range(len(body.clubs)):
        #     body.clubs[i] = ObjectId(body.clubs[i])

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
