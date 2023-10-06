from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import HTTPResponse, text, json
from sanic.request import Request

from app import appserver

import typing


class Events(HTTPMethodView):
    async def get(self, request: Request, id: typing.Union[str, None]):
        ...

    async def post(self, request: Request, id: typing.Union[str, None]):
        ...

    async def patch(self, request: Request, id: typing.Union[str, None]):
        ...

    async def delete(self, request: Request, id: typing.Union[str, None]):
        ...


appserver.add_route(Events.as_view(), "/events/<id:str>")
