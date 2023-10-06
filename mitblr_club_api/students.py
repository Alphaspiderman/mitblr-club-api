from sanic.views import HTTPMethodView
from sanic.response import HTTPResponse, text, json, BaseHTTPResponse
from sanic.request import Request

from app import appserver

import typing


class Students(HTTPMethodView):
    async def get(self, request: Request, id:typing.Union[str, None]):
        ...

    async def post(self, request:Request):
        ...

    async def patch(self, request:Request):
        ...

    async def delete(self, request:Request):
        ...

appserver.add_route(Students.as_view(), "/students")