"""API endpoints for club core committees."""
from typing import Optional
from bson import ObjectId

from sanic import Request, json
from sanic.views import HTTPMethodView
from sanic_ext import validate
from motor.motor_asyncio import AsyncIOMotorCollection

from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.request.team import ClubTeamRequest
from mitblr_club_api.models.enums.core_committee import CoreCommittee

MAX_LENGTH = 100


class ClubsCore(HTTPMethodView):
    """Endpoints regarding core committee of clubs."""

    @authorized_incls
    async def get(self, request: Request, club_slug: str):
        """Get Club's core committee."""

        clubs_collection: AsyncIOMotorCollection = request.app.ctx.db["clubs"]
        club_teams_collection: AsyncIOMotorCollection = request.app.ctx.db["club_teams"]
        student_collection: AsyncIOMotorCollection = request.app.ctx.db["students"]

        core_committee = await clubs_collection.find_one(
            {"slug": club_slug}, {"_id": 0, "core_committee": 1}
        )

        core_committee_members = [
            {"position": position, "student_id": member["student_id"]}
            for position, team_id in core_committee["core_committee"].items()
            for member in await club_teams_collection.find(
                {"_id": ObjectId(team_id)}
            ).to_list(length=MAX_LENGTH)
            if member is not None
        ]

        core_committee_list = [
            {
                "position": member["position"],
                "name": student["name"],
                "application_number": student["application_number"],
                "email": student["email"],
            }
            for member in core_committee_members
            for student in await student_collection.find(
                {"_id": ObjectId(member["student_id"])}
            ).to_list(length=MAX_LENGTH)
        ]

        return json(core_committee_list)

    # TODO - Data Validation
    # TODO - Authentication
    @authorized_incls
    @validate(json=ClubTeamRequest)
    async def post(
        self, request: Request, body: ClubTeamRequest, club_slug: Optional[str]
    ):
        """Add core committee member to the club."""

        auth: AsyncIOMotorCollection = request.app.ctx.db["authentication"]
        clubs: AsyncIOMotorCollection = request.app.ctx.db["clubs"]
        club_teams: AsyncIOMotorCollection = request.app.ctx.db["club_teams"]
        students: AsyncIOMotorCollection = request.app.ctx.db["students"]

        # Checking if student exists in students collection and accessing the student details
        student = await students.find_one(
            {"application_number": body.application_number}
        )

        if student is None:
            d = {"Error Code": "404", "Message": "Student not found."}
            return json(d, status=404)

        # Checking if student is already a part of the club teams
        if (
            await club_teams.find_one(
                {
                    "student_id": student["_id"],
                    "position": body.position,
                    "club": body.club,
                }
            )
            is not None
        ):
            return json(
                {
                    "status": 409,
                    "error": "Conflict",
                    "message": "Student already exists in club_teams collection.",
                },
                status=409,
            )

        # Checking if all permissions are provided
        if all(
            key in body.permissions
            for key in [
                "create_event",
                "modify_event",
                "delete_event",
                "get_event",
                "mark_attendance",
                "modify_attendance",
            ]
        ):
            permissions = {
                "create_event": body.permissions["create_event"],
                "modify_event": body.permissions["modify_event"],
                "delete_event": body.permissions["delete_event"],
                "get_event": body.permissions["get_event"],
                "mark_attendance": body.permissions["mark_attendance"],
                "modify_attendance": body.permissions["modify_attendance"],
            }
        else:
            d = {
                "Error Code": "400",
                "Message": "Bad Request - Permissions not provided.",
            }
            return json(d, status=400)

        # Checking if position information is correctly provided
        if all(key in body.position for key in ["type", "name"]):
            position = {"type": body.position["type"], "name": body.position["name"]}
        else:
            d = {"Error Code": "400", "Message": "Bad Request - Position not provided."}
            return json(d, status=400)

        # Inserting to club_teams collection
        team_doc: dict[str, any] = {
            "api_access": body.api_access,
            "club": body.club,
            "permissions": permissions,
            "position": position,
            "student_id": ObjectId(student["_id"]),
        }

        result = await club_teams.insert_one(team_doc)

        # If core committee member, inserting to core comittee field in clubs collection
        if any(body.position["name"] == member.value for member in CoreCommittee):
            filter = {"name": body.club}
            update = {
                "$set": {
                    f"core_committee.{position['name']}": ObjectId(result.inserted_id)
                }
            }
            await clubs.update_one(filter, update, upsert=True)

        # Inserting to authentication collection if api_access = true
        if body.api_access:
            auth_list = {
                "friendly_name": "TEST_USER",
                "username": body.application_number,
                "auth_type": "USER",
                "student_id": ObjectId(student["_id"]),
                "team_id": ObjectId(result.inserted_id),
            }
            await auth.insert_one(auth_list)

        return json({"Insert": "True", "ObjectId": str(result.inserted_id)})

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: Optional[str]):
        """Update core committee member information."""

    # TODO - Authentication
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete core committee member from the club."""
