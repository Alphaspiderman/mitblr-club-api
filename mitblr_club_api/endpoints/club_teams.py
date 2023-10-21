from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView
from sanic_ext import validate

import jwt
from typing import Optional
from bson import ObjectId

from mitblr_club_api.app import appserver
from mitblr_club_api.decorators.authorized import authorized_incls
from mitblr_club_api.models.club_teams import ClubTeam_Create


class ClubTeams(HTTPMethodView):

    @authorized_incls
    @validate(json=ClubTeam_Create)
    async def post(self, request: Request, body: ClubTeam_Create,uuid: Optional[str]):
        """
        Create a new ClubTeam document in authentication collection, 
        clubs collection and club_teams collection

        """

        #Accessing data from token directly till decorator is made
        payload = jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")

        club_teams = request.app.ctx.db["club_teams"]
        doc = await club_teams.find_one({"student_id": payload["student_id"]})

        if doc:
            d = {"Error Code": "409", "Message": "Conflict - Object already exists"}
            return json(d, status=409)
        
        else:
            clubs = request.app.ctx.db["clubs"]

            if all(key in body.permissions for key in
                    ["create_event",
                      "modify_event", 
                      "delete_event", 
                      "get_event",
                      "mark_attendance",
                      "modify_attendance"]
            ):
                permissions = {
                    "create_event": body.permissions["create_event"],
                    "modify_event": body.permissions["modify_event"],
                    "delete_event": body.permissions["delete_event"],
                    "get_event": body.permissions["get_event"],
                    "mark_attendance": body.permissions["mark_attendance"],
                    "modify_attendance": body.permissions["modify_attendance"]
                }
            else:
                d = {"Error Code": "400", "Message": "Bad Request - Permissions not provided"}
                return json(d, status=400)
            

            if all(key in body.position for key in ["type", "name"]):
                position = {
                    "type": body.position["type"],
                    "name": body.position["name"]
                }
            else:
                d = {"Error Code": "400", "Message": "Bad Request - Position not provided"}
                return json(d, status=400)  


            team_doc: dict[str,any] = {
                "api_access": body.api_access,
                "club": body.club,
                "permissions": permissions,
                "position": position,
                "student_id": ObjectId(payload["student_id"]),
                "auth": ObjectId(payload["auth_id"])
            }

            result = await club_teams.insert_one(team_doc)

            #logic for adding data to clubs collection
            
            core_committee = ["president", "vice_president", "treasurer", "executive_secretary", "general_secretary", "operations_lead"]
            if (position["name"] in core_committee):

                filter = {"name": body.club}
                update =  {"$set":{
                                f"core_committee.{position['name']}" : ObjectId(payload["student_id"])
                            }
                }
                newClub = clubs.update_one(filter, update,upsert=True)

            return json({"Insert": "True", "ObjectId": str(result.inserted_id)})


appserver.add_route(ClubTeams.as_view(), "/club_teams/<uuid:strorempty>")


        