from typing import Optional

from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls


class Events(HTTPMethodView):
    async def get(self, request: Request, slug: Optional[str]):
        """Getting all upcoming events / events by slug."""
        if slug == "":
            # Return events in the next week
            pass
        else:
            # Return event info based on slug
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

    # TODO - Data Validation
    @authorized_incls
    async def post(self, request: Request, slug: str, reg_no: int):
        """Mark Attendance of attendee"""

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
