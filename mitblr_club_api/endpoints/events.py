from sanic.views import HTTPMethodView
from sanic.response import json
from sanic.request import Request

from ..app import appserver

import typing

from ..decorators.authorized import authorized_incls as authorized


class Events(HTTPMethodView):
    async def get(self, request: Request, slug: typing.Union[str, None]):
        """Getting all upcoming events / events by slug"""
        if slug == "":
            # Return events in the next week
            pass
        else:
            # Return event info based on slug
            pass

    # TODO - Data Validation
    @authorized
    async def post(self, request: Request):
        """Creation of Events"""
        ...

    # TODO - Authentication
    # TODO - Scope check (Club Core / Operations)
    @authorized
    async def patch(self, request: Request, slug: typing.Union[str, None]):
        """Updation of Event details / Status"""
        if slug == "":
            d = {"Code": "400", "Message": "Bad Request - Missing Data"}
            return json(d, status=400)

    # TODO - Authentication
    # TODO - Scope Check (Club Core)
    @authorized
    async def delete(self, request: Request, slug: typing.Union[str, None]):
        """Deletion of Events"""
        if slug == "":
            d = {"Code": "400", "Message": "Bad Request - Missing Data"}
            return json(d, status=400)


class Events_Attend(HTTPMethodView):
    @authorized
    async def get(self, request: Request, slug: str, reg_no: int):
        """Check if signed up for event"""
        ...

    # TODO - Data Validation
    @authorized
    async def post(self, request: Request, slug: str, reg_no: int):
        """Mark Attendance of attendee"""
        ...

    # TODO - Data Validation
    # TODO - Scope Check (Club Core / Operations Lead)
    @authorized
    async def patch(self, request: Request, slug: str, reg_no: int):
        """Update Attendance of attendee"""
        ...

    # TODO - Scope Check (Operations Lead)
    @authorized
    async def delete(self, request: Request, slug: str, reg_no: int):
        """Deletion of Events"""
        ...


appserver.add_route(Events.as_view(), "/events/<slug:strorempty>")
appserver.add_route(Events_Attend.as_view(), "/events/<slug:str>/<reg_no:int>")
