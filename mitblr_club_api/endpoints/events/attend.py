"""API endpoints for events attendance."""
from sanic.request import Request
from sanic.response import JSONResponse, json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls


class Events_Attend(HTTPMethodView):
    """Endpoints regarding event attendance."""

    @authorized_incls
    async def get(self, request: Request, slug: str, uuid: int) -> JSONResponse:
        """
        Get a response that given an event slug and student registration number, returns if the student is
        signed up for that event or not.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: str
        :param reg_no: Registration number of the student.
        :type reg_no: int

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
            return json({"Code": "404", "Message": "No Events Found"}, status=404)

        student = await students.find_one(
            {"application_number": str(uuid)}, {"events": 1}
        )

        if not student:
            return json({"Code": "404", "Message": "No Student Found"}, status=404)

        for student_event in student["events"]:
            if student_event["event_id"] == event["_id"]:
                return json(
                    {"Code": "200", "Message": "Student is registered for the event"}
                )

        return json(
            {"Code": "404", "Message": "Student is not registered for the event"},
            status=404,
        )

    # TODO: Data validation.
    @authorized_incls
    async def post(self, request: Request, slug: str, uuid: int) -> JSONResponse:
        """
        Mark the attendance of an event attendee with an event slug and student registration number.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event.
        :type slug: are
        :param reg_no: Registration number of the student.
        :type reg_no: int

        :return: JSON response with code 200 if the student's attendance has been updated. JSON response
                 with code 404 if either the event, or the student is not found, or the student's attendance
                 could not be updated.
        :rtype: JSONResponse
        """

        students = request.app.ctx.db["students"]
        events = request.app.ctx.db["events"]

        event = await events.find_one({"slug": slug})
        if not event:
            return json({"Code": "404", "Message": "No Events Found"}, status=404)

        student = await students.find_one({"application_number": str(uuid)})

        if not student:
            return json({"Code": "404", "Message": "No Student Found"}, status=404)

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
                    {"Code": "200", "Message": "Student attendance has been updated"}
                )

            # TODO: Update on event object in the events collection.
            else:
                # TODO: Mark as on-spot registration.
                pass

        return json(
            {"Code": "404", "Message": "Update Failed"},
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
