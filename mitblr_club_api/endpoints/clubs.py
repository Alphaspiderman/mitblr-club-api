from typing import Optional

from sanic.request import Request
from sanic.views import HTTPMethodView

from mitblr_club_api.app import appserver


class Clubs(HTTPMethodView):
    async def get(self, request: Request, slug: Optional[str]):
        """Retrives club information.

        Args:
            request (Request): _description_
            slug (Optional[str]): _description_
        """
        collection = request.app.ctx.db["clubs"]
        if slug == "":
            # Get all clubs
            # flake8: noqa
            doc = await collection.find({{}, {"coursename": 1}})
            pass
        else:
            # Get specific club
            pass

    # TODO - Data Validation
    # TODO - Authentication
    async def post(self, request: Request, slug: Optional[str]):
        """Create Clubs."""

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: Optional[str]):
        """Update Club information."""

    # TODO - Authentication
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete Club."""


appserver.add_route(Clubs.as_view(), "/clubs/<slug:strorempty>")
