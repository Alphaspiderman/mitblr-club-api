from typing import Optional

from sanic import Request
from sanic.views import HTTPMethodView

from mitblr_club_api.decorators.authorized import authorized_incls


class Clubs_Core(HTTPMethodView):
    """Endpoints regarding core committee of clubs."""

    @authorized_incls
    async def get(self, request: Request, slug: Optional[str]):
        """Get Club's core committee."""

    # TODO - Data Validation
    # TODO - Authentication
    @authorized_incls
    async def post(self, request: Request, slug: Optional[str]):
        """Add core committee member to the club."""

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: Optional[str]):
        """Update core committee member information."""

    # TODO - Authentication
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete core committee member from the club."""
