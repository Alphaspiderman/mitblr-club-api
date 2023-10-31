import bcrypt
import jwt

import motor.motor_asyncio as async_motor
from dotenv import dotenv_values
from sanic import Request, Sanic, response, json
from sanic.log import logger
from sanic_ext import validate

from .app import appserver
from .models.request.login import Login
from .utils import generate_jwt

# noinspection PyUnresolvedReferences
# flake8: noqa
import mitblr_club_api.endpoints


logger.debug("Loading ENV")
config = dotenv_values(".env")

# Read the public and private keys and add them to the config.
with open('public-key.pem') as public_key_file:
    config['PUB_KEY'] = public_key_file.read()

with open('private-key.pem') as private_key_file:
    config['PRIV_KEY'] = private_key_file.read()

# Try to get state from the ENV, defaults to being dev.
is_prod: str = config.get("IS_PROD", "false")

# Convert the string to a bool and update the config with the bool.
config.update({"IS_PROD": is_prod.lower() == "true"})

app: Sanic = appserver
app.config.update(config)


@app.listener("before_server_start")
async def register_db(app: Sanic):
    logger.info("Connecting to MongoDB.")
    connection = app.config.get("MONGO_CONNECTION_URI")

    if connection is None:
        logger.error("Missing MongoDB URL")
        app.stop(terminate=True)

    client = async_motor.AsyncIOMotorClient(
        connection,
        maxIdleTimeMS=10000,
        minPoolSize=10,
        maxPoolSize=50,
        connectTimeoutMS=10000,
        retryWrites=True,
        waitQueueTimeoutMS=10000,
        serverSelectionTimeoutMS=10000,
    )

    logger.info("Connected to MongoDB.")

    # Add MongoDB connection client to ctx for use in other modules.
    app.ctx.db_client = client

    # Check for production environment.
    is_prod = app.config["IS_PROD"]
    if is_prod:
        logger.info("Connected to PRODUCTION")
        app.ctx.db = client["mitblr-club-api"]
    else:
        logger.info("Connected to DEV ENV")
        app.ctx.db = client["mitblr-club-dev"]


@app.listener("after_server_stop")
async def close_connection(app: Sanic, loop):
    app.ctx.db_client.close()
    logger.info("Disconnected from MongoDB")


@app.get("/")
async def get_root(request: Request):
    return response.text("Server Online")


@app.get("/ping")
async def ping_test(request: Request):
    return response.text("Pong")


@app.get("/jwt")
async def jwt_status(request: Request):
    if not request.token:
        d = {"authenticated": False, "message": "No token"}
        return response.json(d)

    try:
        jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")
    except jwt.exceptions.ImmatureSignatureError:
        # Raised when a token’s nbf claim represents a time in the future
        d = {
            "authenticated": False,
            "message": "JWT Token not allowed to be used at time",
        }
        status = 401
    except jwt.exceptions.InvalidIssuedAtError:
        # Raised when a token’s iat claim is in the future
        d = {"authenticated": False, "message": "JWT issues in future"}
        status = 401
    except jwt.exceptions.ExpiredSignatureError:
        # Raised when a token’s exp claim indicates that it has expired
        d = {"authenticated": False, "message": "JWT has expired"}
        status = 401
    except jwt.exceptions.InvalidTokenError:
        # Generic invalid token
        d = {"authenticated": False, "message": "JWT invalid"}
        status = 401
    else:
        # Valid Token
        d = {"authenticated": True, "message": "JWT is valid"}
        status = 200

    return response.json(d, status=status)


@app.post("/login")
@validate(json=Login)
async def login(request: Request, body: Login):
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
                }, status=404
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

            jwt_ = await generate_jwt(app=request.app, data=jwt_data, validity=90)
            json_payload = {"identifier": jwt_, "authenticated": True}

        else:
            # If not verified, return error.
            json_payload = {
                "authenticated": False,
                "message": "Incorrect password",
                "error": "Unauthorized",
            }
            
            status = 401

        return response.json(json_payload, status=status)

    if body.auth_type == "AUTOMATION":
        app_id = body.identifier
        token = body.secret

        collection = request.app.ctx.db["authentication"]
        doc = await collection.find_one({"auth_type": "AUTOMATION", "app_id": app_id})

        if bcrypt.checkpw(token.encode(), doc["token"]):
            # TODO - Add useful data
            jwt_data = {"username": app_id}
            jwt_ = await generate_jwt(app=request.app, data=jwt_data, validity=1440)
            json_payload = {"identifier": jwt_, "authenticated": True}
        else:
            json_payload = {"identifier": app_id, "authenticated": False}

        return response.json(json_payload)


if __name__ == "__main__":
    # Check for Production environment
    is_prod = app.config["IS_PROD"]

    # Use a KWARGS dict to pass to app.run dynamically
    kwargs = {"access_log": True, "host": "0.0.0.0"}

    if is_prod:
        # If prod, check for HOST (internally required for JWTs).
        if app.config.get("HOST") is None:
            logger.error("MISSING HOST")
            quit(1)

    else:
        # If DEV, set HOST to DEV.
        app.config["HOST"] = "DEV"
        kwargs["debug"] = True
        kwargs["auto_reload"] = True

    # Run the API Server
    app.run(**kwargs)
