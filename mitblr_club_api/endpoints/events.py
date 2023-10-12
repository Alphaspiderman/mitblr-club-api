from typing import Optional

from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls

from datetime import datetime, timedelta


class Events(HTTPMethodView):
    async def get(self, request: Request, slug: Optional[str]):
        """Getting all upcoming events / events by slug."""
        collection = request.app.ctx.db["events"]
        if slug == "":
            # Return events in the next week
            now = datetime.utcnow()
            start_date = now
            end_date = now + timedelta(days=7)
            events = await collection.find(
                {"date": {"$gte": start_date, "$lte": end_date}}
            ).to_list(length=100)
            if len(events) == 0:
                return json({"Code": "404", "Message": "No Events Found"}, status=404)
            event_list = []
            for event in events:
                event_list.append(
                    {
                        "name": event["name"],
                        "date": event["date"].isoformat(),
                        "club": event["club"],
                    }
                )

            return json(event_list)
        else:
            # Return event info based on slug
            event = await collection.find_one({"slug": slug})
            if not event:
                return json({"Code": "404", "Message": "No Events Found"}, status=404)
            return json(
                {
                    "name": event["name"],
                    "date": event["date"].isoformat(),
                    "club": event["club"],
                }
            )
            pass

    # TODO - Data Validation
    @authorized_incls
    async def post(self, request: Request):
        """Creation of Events"""

    # TODO - Authentication
    # TODO - Scope check (Club Core / Operations)
    @authorized_incls
    async def patch(self, request: Request, slug: Optional[str]):
        """Updation of Event details / Status"""
        if slug == "":
            d = {"Code": "400", "Message": "Bad Request - Missing Data"}
            return json(d, status=400)

    # TODO - Authentication
    # TODO - Scope Check (Club Core)
    @authorized_incls
    async def delete(self, request: Request, slug: Optional[str]):
        """Deletion of Events"""
        if slug == "":
            d = {"Code": "400", "Message": "Bad Request - Missing Data"}
            return json(d, status=400)


class EventsAttend(HTTPMethodView):
    @authorized_incls
    async def get(self, request: Request, slug: str, reg_no: int):
        """Check if signed up for event"""
        year = request.app.config["SORT_YEAR"]

        students = request.app.ctx.db["students"]
        events = request.app.ctx.db["events"]
        event = await events.find_one({"slug": slug, "sort_year": year})

        if not event:
            return json({"Code": "404", "Message": "No Events Found"}, status=404)
        else:
            id = event["_id"]
        student = await students.find_one(
            {"registration_number": str(reg_no)}, {"events": 1}
        )
        if not student:
            return json({"Code": "404", "Message": "No Student Found"}, status=404)
        else:
            for i in student["events"]:
                if i["event_id"] == id:
                    return json(
                        {
                            "Code": "200",
                            "Message": "Student is registered for the event",
                        },
                        status=200,
                    )

            return json(
                {"Code": "404", "Message": "Student is not registered for the event"},
                status=404,
            )

    # TODO - Data Validation
    @authorized_incls
    async def post(self, request: Request, slug: str, reg_no: int):
        """Mark Attendance of attendee"""
        students = request.app.ctx.db["students"]
        events = request.app.ctx.db["events"]
        event = await events.find_one({"slug": slug})
        if not event:
            return json({"Code": "404", "Message": "No Events Found"}, status=404)
        else:
            id = event["_id"]
        student = await students.find_one({"registration_number": str(reg_no)})
        if not student:
            return json({"Code": "404", "Message": "No Student Found"}, status=404)
        else:
            for event in student["events"]:
                if event["event_id"] == id:
                    query = {
                        "registration_number": str(reg_no),
                        "events.event_id": id,  # Match the specific event_id within the events array
                    }
                    update = {
                        "$set": {  # Update the attendance field of the matched element
                            "events.$.attendance": "true"
                        }
                    }
                    await students.update_one(query, update)
                    return json(
                        {
                            "Code": "200",
                            "Message": "Student attendance has been updated",
                        },
                        status=200,
                    )
                # TODO - Update on Event Object in Events Collection
                else:
                    # TODO - Mark as onspot Registeration
                    pass

            return json(
                {"Code": "404", "Message": "Updation Failed"},
                status=404,
            )

    # TODO - Data Validation
    # TODO - Scope Check (Club Core / Operations Lead)
    @authorized_incls
    async def patch(self, request: Request, slug: str, reg_no: int):
        """Update Attendance of attendee"""

    # TODO - Scope Check (Operations Lead)
    @authorized_incls
    async def delete(self, request: Request, slug: str, reg_no: int):
        """Deletion of Events"""


appserver.add_route(Events.as_view(), "/events/<slug:strorempty>")
appserver.add_route(EventsAttend.as_view(), "/events/<slug:str>/<reg_no:int>")
