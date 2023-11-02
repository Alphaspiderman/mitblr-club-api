"""API endpoints for club core committees."""
from typing import Optional
from bson import ObjectId

from sanic import Request,json
from sanic.views import HTTPMethodView
from motor.motor_asyncio import AsyncIOMotorCollection

from mitblr_club_api.decorators.authorized import authorized_incls

MAX_LENGTH = 100
class ClubsCore(HTTPMethodView):
    """Endpoints regarding core committee of clubs."""

    @authorized_incls
    async def get(self, request: Request, club_slug: str):
        """Get Club's core committee."""
        
        clubs_collection: AsyncIOMotorCollection = request.app.ctx.db["clubs"]
        club_teams_collection: AsyncIOMotorCollection = request.app.ctx.db["club_teams"]
        student_collection: AsyncIOMotorCollection = request.app.ctx.db["students"]
         
        core_committee = await clubs_collection.find_one({"slug": club_slug},{"_id":0,"core_committee":1})

        core_committee_members = [
            {
                "position" : position,
                "student_id" : member["student_id"]
            } for position,team_id in core_committee["core_committee"].items() 
              for member in await club_teams_collection.find({"_id":ObjectId(team_id)}).to_list(length=MAX_LENGTH)
              if member is not None
        ]


        core_committee_list = [
            {
                "position" : member["position"],
                "name": student["name"],
                "application_number": student["application_number"],
                "email": student["email"]
            } for member in core_committee_members
              for student in await student_collection.find({"_id":ObjectId(member["student_id"])}).to_list(length=MAX_LENGTH)
        ]

        print(core_committee_list)

        return json(core_committee_list)
            
            
                      


    # TODO - Data Validation
    # TODO - Authentication
    @authorized_incls
    async def post(self, request: Request, slug: Optional[str]):
        """Add core committee member to the club."""

    # TODO - Data Validation
    # TODO - Authentication
    async def patch(self, request: Request, slug: Optional[str]):
        """Update core committee member information."""

    # TODO - Authentication
    async def delete(self, request: Request, slug: Optional[str]):
        """Delete core committee member from the club."""
