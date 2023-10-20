from typing import Optional

from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.response import json
from sanic_ext import validate


from mitblr_club_api.app import appserver

from mitblr_club_api.models.clubs import Club_Create
from mitblr_club_api.decorators.authorized import authorized_incls


class Clubs(HTTPMethodView):
    @authorized_incls
    async def get(self, request: Request, slug: Optional[str]):
        """Get Club Info"""
        collection = request.app.ctx.db["clubs"]
        if slug == "":
            # Get all clubs
            # flake8: noqa
            docs = await collection.find({}).to_list(length=100)

            if docs is None:
                return json({"Code": "404", "Message": "No Clubs Found"}, status=404)
            else:
                club_list = []
                for doc in docs:
                    club_list.append(
                        {
                            "club": doc["name"],
                            "slug": doc["slug"],
                            "unit": doc["unit_type"],
                            "institution": doc["institution"],
                        }
                    )

                return json(club_list)

        else:
            # Get specific club
            doc = await collection.find_one({"slug": slug})
            if not doc:
                return json({"Code": "404", "Message": "No Clubs Found"}, status=404)
            else:
                return json(
                    {
                        "club": doc["name"],
                        "slug": doc["slug"],
                        "unit": doc["unit_type"],
                        "institution": doc["institution"],
                    }
                )

    # TODO - Data Validation
    # TODO - Authentication

    @authorized_incls
    @validate(json=Club_Create)
    async def post(self, request: Request, body: Club_Create, slug: Optional[str]):
        """Create Clubs"""
        collection = request.app.ctx.db["clubs"]
        doc = await collection.find_one({"slug": body.slug})

        # Making a new list to enter only the required fields into the faculty_advisors field
        faculty_advisors = list()
        for faculty in body.faculty_advisors:
            if ("name" not in faculty) or ("email" not in faculty):
                d = {"Error Code": "500", "Message": "All required fields not present"}
                return json(d, status=500)
            faculty_advisors.append(
                {"name": faculty["name"], "email": faculty["email"]}
            )

        if doc is None:
            club = dict()
            club["name"] = body.name
            club["slug"] = body.slug
            club["unit_type"] = body.unit_type.value
            club["institution"] = body.institution
            club["faculty_advisors"] = faculty_advisors
            club["core_committee"] = {}
            club["events"] = {}
            club["operations"] = []
            result = await collection.insert_one(club)
            d = {"Insert": "True", "ObjectId": str(result.inserted_id)}
            return json(d)

        else:
            d = {"Error Code": "409", "Message": "Conflict - Object already exists"}
            return json(d, status=409)

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: Optional[str]):
        """Update Club information"""

    # TODO - Authentication
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete Club"""


appserver.add_route(Clubs.as_view(), "/clubs/<slug:strorempty>")
