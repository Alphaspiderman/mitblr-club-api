from sanic import Blueprint
from sanic.views import HTTPMethodView
from sanic.response import HTTPResponse, text, json
from sanic.request import Request

from app import appserver

import typing

class Clubs(HTTPMethodView):
    async def get(self, request: Request):
        ...

    async def post(self, request: Request):
        ...

    async def patch(self, request: Request):
        ...

    async def delete(self, request: Request):
        ...

appserver.add_route(Clubs.as_view(), "/students")