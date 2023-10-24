"""API endpoints for events"""
from typing import Optional

from datetime import datetime, timedelta

from sanic.request import Request
from sanic.response import JSONResponse, json
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls


class Events(HTTPMethodView):
    """Endpoints regarding events."""

    async def get(self, request: Request, slug: str) -> JSONResponse:
        """
        Get a response with either all the events for the next week if there is no slug, or a particular event
        referenced to by the slug.

        :param request: Sanic request.
        :type request: Request
        :param slug: Slug for the event, or an empty string.
        :type slug: str

        :return: Returns JSON with either the event corresponding to the slug, or all the events for the
                 next week if the slug is an empty string. JSON with code 404 if the event does not exist
                 in either slug case.
        :rtype: JSONResponse
        """

        collection = request.app.ctx.db["events"]

        if slug == "":
            # Slug is empty, return the events in the next week.
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)

            events = await collection.find(
                {"date": {"$gte": start_date, "$lte": end_date}}
            ).to_list(length=100)

            if len(events) == 0:
                return json({"Code": "404", "Message": "No Events Found"}, status=404)

            return json(
                [
                    {
                        "name": event["name"],
                        "date": event["date"].isoformat(),
                        "club": event["club"],
                    }
                    for event in events
                ]
            )

        else:
            # Return event info based on the slug.
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
