"""API endpoints for events"""
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient
from sanic.request import Request
from sanic.response import JSONResponse, json
from sanic.views import HTTPMethodView

from mitblr_club_api.endpoints import MAX_LENGTH

class Events(HTTPMethodView):
    """Endpoints regarding events."""

    async def get(self, request: Request, event_slug: str):
        """
        Get a response with either all the events for the next week if there is no slug, or a particular event
        referenced to by the slug.

        :param request: Sanic request.
        :type request: Request
        :param event_slug: Slug for the event, or an empty string.
        :type event_slug: str

        :return: Returns JSON with either the event corresponding to the slug, or all the events for the
                 next week if the slug is an empty string. JSON with code 404 if the event does not exist
                 in either slug case.
        :rtype: JSONResponse
        """

        collection: AsyncIOMotorClient = request.app.ctx.db["events"]

        if event_slug == "":
            # Slug is empty, return the events in the next week.
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)

            events = await collection.find(
                {"date": {"$gte": start_date, "$lte": end_date}}
            ).to_list(length=MAX_LENGTH)

            if len(events) == 0:
                return json(
                    {"status": 404, "error": "Not Found", "message": "No events found."},
                    status=404,
                )

            events_ = [
                {
                    "name": event["name"],
                    "date": event["date"].isoformat(),
                    "club": event["club"]
                } for event in events
            ]

            return json(events_)

        else:
            # Return event info based on the slug.
            event = await collection.find_one({"slug": event_slug})

            if not event:
                return json(
                    {"status": 404, "error": "Not Found", "message": "No events found."},
                    status=404,
                )

            return json(
                {
                    "name": event["name"],
                    "date": event["date"].isoformat(),
                    "club": event["club"],
                }
            )
