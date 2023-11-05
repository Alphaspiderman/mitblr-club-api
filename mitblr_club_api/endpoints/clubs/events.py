"""API endpoints for club events."""
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.request.events import EventRequest


class ClubEvents(HTTPMethodView):
    """Endpoints regarding events from the club."""

    @authorized_incls
    async def get(self, request: Request, club_slug: str, event_slug: Optional[str]):
        """Get Events from the Club"""

    # TODO - Check valid Club Slug
    # TODO - Check JWT Scope for Club
    # TODO - Check JWT for creation permissions
    @authorized_incls
    @validate(json=EventRequest)
    async def post(
        self,
        request: Request,
        body: EventRequest,
        club_slug: str,
        event_slug: Optional[str],
    ):
        """
        Create a new event in the database.

        :param request: Sanic request.
        :type request: Request
        :param body: Event information.
        :type body: EventRequest
        :param club_slug: Slug for the club.
        :type club_slug: str
        :param event_slug: Slug for the newly created event.
        :type event_slug: Optional[str]

        :return: Response with status whether the event is created or not.
        :rtype: JSONResponse
        """

        data = body.model_dump()
        sort_year = request.app.config["SORT_YEAR"]

        # Converting the event name into a compliant slug.
        sub_slug = data["name"].lower().replace(" ", "-")

        event_slug = f"{club_slug}-{sub_slug}"

        # Check if event already exists based on event slug and sort year.
        collection: AsyncIOMotorCollection = request.app.ctx.db["events"]

        event = await collection.find_one(
            {"$and": [{"slug": event_slug}, {"sort_year": str(sort_year)}]}
        )

        if event:
            return json(
                {
                    "status": 409,
                    "error": "Conflict",
                    "message": "Event already exists.",
                },
                status=409,
            )

        data["sort_year"] = sort_year
        data["club"] = club_slug
        data["slug"] = event_slug

        result = await collection.insert_one(data)

        return json(
            {
                "status": 201,
                "message": "Event created.",
                "id": str(result.inserted_id),
                "slug": event_slug,
            },
            status=201,
        )

    # TODO - Data Validation
    # TODO - Permission Check
    async def patch(
        self, request: Request, body: EventRequest, club_slug: str, event_slug: str
    ):
        """Update Event information"""

    # TODO - Permission Check
    async def delete(self, request: Request, club_slug: str, event_slug: str):
        """Delete Event"""
