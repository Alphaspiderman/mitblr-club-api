"""API endpoints for events"""
from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView


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

        if event_slug == "":
            # Slug is empty, return the events in the next week.
            events = await request.app.ctx.cache.get_event_by_timedelta(delta=7)

            if events:
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

            return json(
                {
                    "status": 404,
                    "error": "Not Found",
                    "message": "No events found.",
                },
                status=404,
            )

        else:
            # Return event info based on the slug.
            event = await request.app.ctx.cache.get_event(event_slug)

            if event:
                return json(
                    {
                        "name": event["name"],
                        "date": event["date"].isoformat(),
                        "club": event["club"],
                    }
                )
            return json(
                {
                    "status": 404,
                    "error": "Not Found",
                    "message": "No events found.",
                },
                status=404,
            )
