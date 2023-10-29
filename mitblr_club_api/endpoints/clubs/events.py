from typing import Optional

from sanic import Request
from sanic.views import HTTPMethodView
from sanic_ext import validate
from sanic.response import json

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.request.events import Event_Request


class Club_Events(HTTPMethodView):
    """Endpoints regarding events from the club."""

    @authorized_incls
    async def get(self, request: Request, club_slug: str, event_slug: Optional[str]):
        """Get Events from the Club"""

    # TODO - Check valid Club Slug
    # TODO - Check JWT Scope for Club
    # TODO - Check JWT for creation permissions
    @authorized_incls
    @validate(json=Event_Request)
    async def post(
        self,
        request: Request,
        body: Event_Request,
        club_slug: str,
        event_slug: Optional[str],
    ):
        """Create Event under the Club"""
        # Convert the body to a dict
        data = body.model_dump()
        # Define variables required for event check and creation
        sort_year = request.app.config["SORT_YEAR"]
        sub_slug = data["name"].lower().replace(" ", "-")
        # Save and override the event slug
        event_slug = f"{club_slug}-{sub_slug}"
        # Check if event already exists based on event slug and sort year
        collection = request.app.ctx.db["events"]
        doc = await collection.find(
            {"$and": [{"slug": event_slug}, {"sort_year": str(sort_year)}]}
        ).to_list(length=1)
        if doc:
            return json(
                {"status": 409, "error": "Conflict", "message": "Event already exists"},
                status=409,
            )
        # No event exists, create a new event
        # Set sort year from config
        data["sort_year"] = sort_year
        # Set the club slug
        data["club"] = club_slug
        # Set the event slug
        data["slug"] = event_slug
        # Push data to MongoDB
        collection = request.app.ctx.db["events"]
        result = await collection.insert_one(data)
        # Return the confirmation as a JSON response
        return json(
            {
                "status": 201,
                "message": "Event created",
                "id": str(result.inserted_id),
                "slug": event_slug,
            },
            status=201,
        )

    # TODO - Data Validation
    # TODO - Permission Check
    async def patch(
        self, request: Request, body: Event_Request, club_slug: str, event_slug: str
    ):
        """Update Event information"""

    # TODO - Permission Check
    async def delete(self, request: Request, club_slug: str, event_slug: str):
        """Delete Event"""
