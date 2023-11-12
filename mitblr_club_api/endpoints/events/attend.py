"""API endpoints for events attendance."""
from motor.motor_asyncio import AsyncIOMotorClient
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.cached.events import EventCache
from mitblr_club_api.models.cached.students import StudentCache


class EventsAttend(HTTPMethodView):
    """Endpoints regarding event attendance."""

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

        events = request.app.ctx.db["events"]

        # Unable to Cache due to attendance being on the object.
        event: EventCache = await events.find_one({"slug": slug, "sort_year": year})

        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student: StudentCache = await request.app.ctx.cache.get_student(uuid)

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

        :return: JSON response with code 200 if the student's attendance has been updated. JSON response
                 with code 404 if either the event, or the student is not found, or the student's attendance
                 could not be updated.
        :rtype: JSONResponse
        """

        students: AsyncIOMotorClient = request.app.ctx.db["students"]

        # Can used cached event object due to no data modification.
        event: EventCache = await request.app.ctx.cache.get_event(slug)

        if not event:
            return json(
                {"status": 404, "error": "Not Found", "message": "No events found."},
                status=404,
            )

        student: StudentCache = await request.app.ctx.cache.get_student(int(uuid))

        if not student:
            return json(
                {"status": 404, "error": "Not Found", "message": "No student found."},
                status=404,
            )

        event_id = event["_id"]

        for event in student["events"]:
            if event["event_id"] == event_id:
                # Match the specific event_id within the events array.
                query = {
                    "application_number": str(uuid),
                    "events.event_id": event_id,
                }

                # Update the attendance field of the matched element.
                update = {"$set": {"events.$.attendance": "true"}}

                await students.update_one(query, update)
                return json(
                    {"status": 200, "message": "Student attendance has been updated."}
                )

            # TODO: Update on event object in the events collection.
            else:
                # TODO: Mark as on-spot registration.
                pass

        return json(
            {"status": 404, "error": "Not Found", "message": "Update failed."},
            status=404,
        )

    # TODO - Data Validation
    # TODO - Scope Check (Club Core / Operations Lead)
    @authorized_incls
    async def patch(self, request: Request, slug: str, uuid: int):
        """Update Attendance of attendee"""

    # TODO - Scope Check (Operations Lead)
    @authorized_incls
    async def delete(self, request: Request, slug: str, uuid: int):
        """Deletion of Events"""
