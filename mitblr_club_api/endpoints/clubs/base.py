from typing import Optional

from sanic import Request, json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.request.club import Club_Request


class Clubs(HTTPMethodView):
    @authorized_incls
    async def get(self, request: Request, club_slug: Optional[str]):
        """Get Club Info"""
        collection = request.app.ctx.db["clubs"]
        if club_slug == "":
            # Get all clubs
            docs = await collection.find({}).to_list(length=100)

            if docs is None:
                return json({"status": 404, "message": "No clubs found"}, status=404)
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
            doc = await collection.find_one({"slug": club_slug})
            if not doc:
                return json(
                    {"status": 404, "error": "Not Found", "message": "No clubs found"},
                    status=404,
                )
            else:
                return json(
                    {
                        "club": doc["name"],
                        "slug": doc["slug"],
                        "unit": doc["unit_type"],
                        "institution": doc["institution"],
                    }
                )

    @authorized_incls
    @validate(json=Club_Request)
    async def post(
        self, request: Request, body: Club_Request, club_slug: Optional[str]
    ):
        """Create Clubs"""
        collection = request.app.ctx.db["clubs"]
        doc = await collection.find_one({"slug": body.slug})

        # Making a new list to enter only the required fields into the faculty_advisors field
        faculty_advisors = list()
        for faculty in body.faculty_advisors:
            if ("name" not in faculty) or ("email" not in faculty):
                d = {"status": 500, "message": "All required fields not present"}
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
            d = {"status": 409, "error": "Conflict", "message": "Object already exists"}
            return json(d, status=409)

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, club_slug: Optional[str]):
        """Update Club information"""

    # TODO - Authentication
    async def delete(self, request: Request, club_slug: Optional[str]):
        """Delete Club"""
