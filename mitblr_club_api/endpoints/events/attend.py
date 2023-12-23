"""API endpoints for events attendance."""
from motor.motor_asyncio import AsyncIOMotorClient
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.cached.events import EventCache

# from mitblr_club_api.models.cached.students import StudentCache
from mitblr_club_api.models.internal.students import Student

from bson import ObjectId


class EventsAttend(HTTPMethodView):
    """Endpoints regarding event attendance."""

    @authorized_incls
    async def get(self, request: Request, slug: str, uuid: int):
        """
        Get a response that given an event slug and student application number, returns if the student
        attended the event or not.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: str
        :param uuid: Application number of the student.
        :type uuid: int

        :return: JSON response with code 200 if the student attended the event. JSON response with
                 code 404 if either the event, or the student is not found, or if the student did
                 not attend the event.
        :rtype: JSONResponse
        """

        year = request.app.config["SORT_YEAR"]
        students = request.app.ctx.db["students"]

        # Unable to Cache due to attendance being on the object.
        event: EventCache = await request.app.ctx.cache.get_event(
            event_slug=slug, year=year
        )

        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student = await students.find_one({"application_number": uuid}, {"events": 1})
        student: Student = Student(
            **await students.find_one(
                {
                    "application_number": uuid,
                }
            )
        )

        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        for id in event["participants"]["attended"]:
            if id == student["_id"]:
                return json({"status": 200, "message": "Student attended the event."})

        return json(
            {
                "status": 404,
                "error": "Not Found",
                "message": "Student did not attend the event.",
            },
            status=404,
        )

    # TODO: Data validation.
    @authorized_incls
    async def post(self, request: Request, slug: str, uuid: int):
        """
        Mark the attendance of an event attendee with an event slug and student application number.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: are
        :param uuid: Application number of the student.
        :type uuid: int

        :return: JSON response with code 200 if the student's attendance has been updated or if registration
                 is onspot. JSON response with code 404 if either the event, or the student is not found, or
                 the student's attendance could not be updated. JSON response with code 409 if the student's
                 attendance is already marked.
        :rtype: JSONResponse
        """

        students: AsyncIOMotorClient = request.app.ctx.db["students"]
        events: AsyncIOMotorClient = request.app.ctx.db["events"]

        # Can used cached event object due to no data modification.
        event: EventCache = await request.app.ctx.cache.get_event(slug)

        # Checking if event exists
        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        # TODO - Timed Cache
        student = await students.find_one({"application_number": uuid})

        # Checking if student exists
        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        # student_db = await students.find_one(
        #     {
        #         "application_number": student.application_number,
        #     }
        # )

        event_id = event["_id"]

        # Checking if student attendance is already marked
        for attendee in event["participants"]["attended"]:
            if attendee == student["_id"]:
                return json(
                    {
                        "status": 409,
                        "error": "Conflict",
                        "message": "Student attendance is already marked.",
                    },
                    status=409,
                )

        # Updating attendance in events field in student document in students collection
        for event in student["events"]:
            if event["event_id"] == event_id:
                # Match the specific event_id within the events array.
                query = {
                    "application_number": student.application_number,
                    "events.event_id": event_id,
                }

                # Update the attendance field of the matched element.
                update = {"$set": {"events.$.attended": True}}

                await students.update_one(query, update)

                # Update on event object in the events collection.
                await events.update_one(
                    {"_id": event_id},
                    {"$push": {"participants.attended": ObjectId(student["_id"])}},
                )
                return json(
                    {"status": 200, "message": "Student attendance has been updated."}
                )

            else:
                # TODO: Mark as on-spot registration.
                pass

        # Register student as onspot
        await students.update_one(
            {"application_number": uuid},
            {
                "$push": {
                    "events": {
                        "event_id": event_id,
                        "registration": "onspot",
                        "sort_year:": request.app.config["SORT_YEAR"],
                        "attended": True,
                    }
                }
            },
        )

        # Update registered students in event collection
        await events.update_one(
            {"_id": event_id},
            {
                "$push": {
                    "participants.registered": ObjectId(student["_id"]),
                    "participants.attended": ObjectId(student["_id"]),
                }
            },
        )

        return json(
            {
                "status": 200,
                "message": "Student has been been given onspot registration.",
            }
        )

    # TODO - Data Validation
    # TODO - Scope Check (Club Core / Operations Lead)
    @authorized_incls
    async def patch(self, request: Request, slug: str, uuid: int):
        """Update Attendance of attendee"""

    # TODO - Scope Check (Operations Lead)
    @authorized_incls
    async def delete(self, request: Request, slug: str, uuid: int):
        """Deletion of Attendance"""

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
                # Update attendance in student collection
                await students.update_one(
                    {"application_number": uuid},
                    {"$set": {"events.$[].attended": False}},
                )

                # Update attendeded students in event collection

                # Delete from attended
                await events.update_one(
                    {"_id": event["_id"]},
                    {"$pull": {"participants.attended": ObjectId(student["_id"])}},
                )

                return json(
                    {"status": 200, "message": "Student attendance removed from event."}
                )

        return json(
            {
                "status": 404,
                "error": "Not Found",
                "message": "Student is not attending the event.",
            },
        )
