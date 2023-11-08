"""API endpoints for events registrations."""
from motor.motor_asyncio import AsyncIOMotorClient
from sanic.request import Request
from sanic.response import JSONResponse, json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls


class EventsRegister(HTTPMethodView):
    """Endpoints regarding event registrations."""

    @authorized_incls
    async def get(self, request: Request, slug: str, uuid: int):
        """
        Get a response that given an event slug and student application number, returns if the student is
        signed up for that event or not.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: str
        :param uuid: Application number of the student.
        :type uuid: int

        :return: JSON response with code 200 if the student is registered for the event. JSON response with
                 code 404 if either the event, or the student is not found, or the student is not registered
                 for the event.
        :rtype: JSONResponse
        """

        year = request.app.config["SORT_YEAR"]

        students = request.app.ctx.db["students"]
        events = request.app.ctx.db["events"]

        event = await events.find_one({"slug": slug, "sort_year": year})

        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student = await students.find_one(
            {"application_number": str(uuid)}, {"events": 1}
        )

        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        for student_event in student["events"]:
            if student_event["event_id"] == event["_id"]:
                return json(
                    {"status": 200, "message": "Student is registered for the event."}
                )

        return json(
            {
                "status": 404,
                "error": "Not Found",
                "message": "Student is not registered for the event.",
            },
            status=404,
        )
