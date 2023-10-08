from sanic.views import HTTPMethodView
from sanic.response import HTTPResponse, text, json
from sanic.request import Request

from app import appserver

import typing


class Clubs(HTTPMethodView):
    async def get(self, request: Request, slug: typing.Union[str, None]):
        """Get Club Info"""
        collection = request.app.ctx.db["clubs"]
        if slug == "":
            # Get all clubs
            doc = await collection.find({{}, {"coursename": 1}})
            pass
        else:
            # Get specific club
            pass

    # TODO - Data Validation
    # TODO - Authentication
    async def post(self, request: Request, slug: typing.Union[str, None]):
        """Create Clubs"""
        ...

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: typing.Union[str, None]):
        """Update Club information"""
        ...

    # TODO - Authentication
    async def delete(self, request: Request, slug: typing.Union[str, None]):
        """Delete Club"""
        ...


appserver.add_route(Clubs.as_view(), "/clubs/<slug:strorempty>")
