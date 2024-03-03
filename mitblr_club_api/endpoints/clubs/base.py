"""API endpoints for clubs."""
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Request, json
from sanic.views import HTTPMethodView
from sanic_ext import validate

from mitblr_club_api.decorators.authorized import authorized
from mitblr_club_api.models.cached.clubs import ClubCache
from mitblr_club_api.models.request.club import ClubRequest

MAX_LENGTH = 100


class Clubs(HTTPMethodView):
    @authorized()
    async def get(self, request: Request, club_slug: Optional[str]):
        """
        Get the club information given its slug. If the slug is empty, get the information of every club.

        :param request: Sanic request.
        :type request: Request
        :param club_slug: Slug for the club.
        :type club_slug: str

        :return: Response with club information.
        :rtype: JSONResponse
        """

        if club_slug == "":
            # Get all clubs.
            clubs: list[ClubCache] = request.app.ctx.cache.get_clubs()

            if clubs is None:
                return json(
                    {"status": 404, "error": "Not Found", "message": "No clubs found."},
                    status=404,
                )

            club_list = [
                {
                    "club": club.name,
                    "slug": club.slug,
                    "unit": club.unit_type.name,
                    "institution": club.institution,
                }
                for club in clubs
            ]

            return json(club_list)

        else:
            # Get a specific club.
            club: ClubCache = await request.app.ctx.cache.get_club(club_slug)

            if not club:
                return json(
                    {"status": 404, "error": "Not Found", "message": "No clubs found."},
                    status=404,
                )

            return json(
                {
                    "club": club.name,
                    "slug": club.slug,
                    "unit": club.unit_type.name,
                    "institution": club.institution,
                }
            )

    @authorized()
    @validate(json=ClubRequest)
    async def post(self, request: Request, body: ClubRequest, club_slug: Optional[str]):
        """
        Create a new club in the database.

        :param request: Sanic request.
        :type request: Request
        :param body: Club information.
        :type body: ClubRequest
        :param club_slug: Slug for the newly created club.
        :type club_slug: Optional[str]

        :return: Response with status whether the club is created or not.
        :rtype: JSONResponse
        """

        collection: AsyncIOMotorCollection = request.app.ctx.db["clubs"]

        club: ClubCache = await request.app.ctx.cache.get_club(body.slug)

        # Making a new list to enter only the required fields into the faculty_advisors field.
        faculty_advisors = list()
        for faculty in body.faculty_advisors:
            if "name" not in faculty or "email" not in faculty:
                return json(
                    {"status": 500, "message": "Required fields not present."},
                    status=500,
                )

            faculty_advisors.append(
                {"name": faculty["name"], "email": faculty["email"]}
            )

        if club is None:
            club = {
                "name": body.name,
                "slug": body.slug,
                "unit_type": body.unit_type.value,
                "institution": body.institution,
                "faculty_advisors": faculty_advisors,
                "core_committee": {},
                "events": {},
                "operations": [],
            }

            result = await collection.insert_one(club)
            return json({"Insert": "True", "ObjectId": str(result.inserted_id)})

        return json(
            {"status": 409, "error": "Conflict", "message": "Object already exists."},
            status=409,
        )

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, club_slug: Optional[str]):
        """Update Club information"""

    # TODO - Authentication
    async def delete(self, request: Request, club_slug: Optional[str]):
        """Delete Club"""
