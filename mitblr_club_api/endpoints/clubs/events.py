from typing import Optional

from sanic import Request
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.events import Event


class Club_Events(HTTPMethodView):
    """Endpoints regarding events from the club."""

    @authorized_incls
    async def get(self, request: Request, slug: Optional[str]):
        """Get Events from the Club"""

    # TODO - Data Validation
    # TODO - Permission Check
    @authorized_incls
    @validate(json=Event)
    async def post(self, request: Request, body: Event, slug: Optional[str]):
        """Create Event under the Club"""

    # TODO - Data Validation
    # TODO - Permission Check
    async def patch(self, request: Request, slug: Optional[str]):
        """Update Event information"""

    # TODO - Permission Check
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete Event"""
