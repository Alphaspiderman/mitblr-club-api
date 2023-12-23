"""API endpoints for events registrations."""
from motor.motor_asyncio import AsyncIOMotorClient
from sanic.request import Request
from sanic.response import JSONResponse, json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls

from bson import ObjectId


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

        student = await students.find_one({"application_number": uuid}, {"events": 1})

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

    @authorized_incls
    async def post(self, request: Request, slug: str, uuid: int):
        """
        Post a response that given an event slug and student application number, registers the student for
        that event.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: str
        :param uuid: Application number of the student.
        :type uuid: int

        :return: JSON response with code 200 if the student is registered for the event. JSON response with
                 code 404 if either the event, or the student is not found, or the student is not registered
                 for the event. JSON response with code 409 if student is already registered for the event.
        :rtype: JSONResponse
        """

        year = request.app.config["SORT_YEAR"]

        students: AsyncIOMotorClient = request.app.ctx.db["students"]
        events: AsyncIOMotorClient = request.app.ctx.db["events"]

        event = await events.find_one({"slug": slug, "sort_year": year})

        # Check if event exists
        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student = await students.find_one({"application_number": uuid}, {"events": 1})

        # Check if student exists
        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        # Check if student is already registered
        for student_event in student["events"]:
            if student_event["event_id"] == event["_id"]:
                return json(
                    {
                        "status": 200,
                        "message": "Student is already registered for the event.",
                    }
                )

        # Register student for event
        await students.update_one(
            {"application_number": uuid},
            {
                "$push": {
                    "events": {
                        "event_id": event["_id"],
                        "registration": "time",
                        "sort_year:": request.app.config["SORT_YEAR"],
                        "attended": False,
                    }
                }
            },
        )

        # Update registered students in event collection
        await events.update_one(
            {"_id": event["_id"]},
            {"$push": {"participants.registered": ObjectId(student["_id"])}},
        )

        return json(
            {"status": 200, "message": "Student has been registered for event."}
        )

    # TODO - Scope Check (Operations Lead)
    @authorized_incls
    async def delete(self, request: Request, slug: str, uuid: int):
        """Deletion of Registrations"""

        year = request.app.config["SORT_YEAR"]

        students: AsyncIOMotorClient = request.app.ctx.db["students"]
        events: AsyncIOMotorClient = request.app.ctx.db["events"]

        event = await events.find_one({"slug": slug, "sort_year": year})

        # Check if event exists
        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student = await students.find_one({"application_number": uuid}, {"events": 1})

        # Check if student exists
        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        # Check if student is registered
        for student_event in student["events"]:
            if student_event["event_id"] == event["_id"]:
                # Remove student from event
                await students.update_one(
                    {"application_number": uuid},
                    {"$pull": {"events": {"event_id": event["_id"]}}},
                )

                # Update registered students in event collection

                # Delete from registered
                await events.update_one(
                    {"_id": event["_id"]},
                    {"$pull": {"participants.registered": ObjectId(student["_id"])}},
                )

                # Delete from attended
                await events.update_one(
                    {"_id": event["_id"]},
                    {"$pull": {"participants.attended": ObjectId(student["_id"])}},
                )

                return json(
                    {
                        "status": 200,
                        "message": "Student has been unregistered from event.",
                    }
                )

        return json(
            {
                "status": 404,
                "error": "Not Found",
                "message": "Student is not registered for the event.",
            },
        )
