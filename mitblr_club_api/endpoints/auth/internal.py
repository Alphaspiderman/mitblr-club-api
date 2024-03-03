"""API endpoints for internal authentication provider."""
import bcrypt
from sanic import Request, json
from sanic.views import HTTPMethodView
from sanic_ext import validate
from mitblr_club_api.models.request.login import Login
from mitblr_club_api.utils import generate_jwt

MAX_LENGTH = 100


class InternalAuth(HTTPMethodView):
    @validate(json=Login)
    async def post(self, request: Request, body: Login):
        status = 200

        if body.auth_type == "USER":
            user = body.identifier
            password = body.secret

            collection = request.app.ctx.db["authentication"]
            doc = await collection.find_one({"auth_type": "USER", "username": user})

            # Check if user exists
            if doc is None:
                return json(
                    {
                        "authenticated": False,
                        "message": "User not found",
                        "error": "Not Found",
                    },
                    status=404,
                )

            password_hash = doc.get("password_hash")

            # We are not sure if we are going to be omitting the password_hash field on the
            # document or setting the field as empty. So we check for both cases.
            if password_hash is None or password_hash == b"":
                # Operations team password setup.
                # Generate a hash for the password and store it in the database
                password_hash = bcrypt.hashpw(password.encode(), salt=bcrypt.gensalt())

                # Upsert password hash to MongoDB.
                await collection.update_one(
                    {"auth_type": "USER", "username": user},
                    {"$set": {"password_hash": password_hash}},
                    upsert=True,
                )

                # Set verified to True (only for first time login).
                verified = True
            else:
                # Verify the password for existing users.
                verified = bcrypt.checkpw(password.encode(), password_hash)

            # If verified, generate JWT.
            if verified:
                jwt_data = {
                    "auth_id": str(doc["_id"]),
                    "student_id": str(doc["student_id"]),
                    "team_id": str(doc["team_id"]),
                }

                jwt_ = await generate_jwt(
                    app=request.app,
                    data=jwt_data,
                    validity=90,
                    target="external",
                )
                json_payload = {"identifier": jwt_, "authenticated": True}

                # Fetch and cache team data.
                await request.app.ctx.cache.fetch_team(jwt_data["team_id"])

            else:
                # If not verified, return error.
                json_payload = {
                    "authenticated": False,
                    "message": "Incorrect password",
                    "error": "Unauthorized",
                }

                status = 401

            return json(json_payload, status=status)

        if body.auth_type == "AUTOMATION":
            app_id = body.identifier
            token = body.secret

            collection = request.app.ctx.db["authentication"]
            doc = await collection.find_one(
                {"auth_type": "AUTOMATION", "app_id": app_id}
            )

            if bcrypt.checkpw(token.encode(), doc["token"]):
                # TODO - Add useful data
                jwt_data = {"username": app_id}
                jwt_ = await generate_jwt(
                    app=request.app, data=jwt_data, validity=1440, target="automation"
                )
                json_payload = {"identifier": jwt_, "authenticated": True}
            else:
                json_payload = {"identifier": app_id, "authenticated": False}

            return json(json_payload)
