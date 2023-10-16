import bcrypt
import motor.motor_asyncio as async_motor
from dotenv import dotenv_values
from sanic import Request, Sanic, response
from sanic.log import logger
from sanic_ext import validate

from .app import appserver
from .models.login_data import LoginData
from .utils.generate_jwt import generate_jwt

# noinspection PyUnresolvedReferences
# flake8: noqa
from mitblr_club_api.endpoints import clubs, events, students

import jwt

logger.debug("Loading ENV")
config = dotenv_values(".env")


pub = open("public-key.pem", "r")
priv = open("private-key.pem", "r")
config["PUB_KEY"] = pub.read()
config["PRIV_KEY"] = priv.read()

pub.close()
priv.close()

app: Sanic = appserver
app.config.update(config)


@app.listener("before_server_start")
async def register_db(app: Sanic):
    logger.info("Connecting to MongoDB")
    # Get Mongo Connection URL
    connection = app.config.get("MONGO_CONNECTION_URI", None)
    if connection is None:
        logger.error("Missing MongoDB URL")
        app.stop(terminate=True)
    # Create a database connection pool
    client = async_motor.AsyncIOMotorClient(
        connection,
        # in milliseconds
        maxIdleTimeMS=10000,
        # minimal pool size
        minPoolSize=10,
        # maximal pool size
        maxPoolSize=50,
        # connection timeout in milliseconds
        connectTimeoutMS=10000,
        # boolean
        retryWrites=True,
        # wait queue in milliseconds
        waitQueueTimeoutMS=10000,
        # in milliseconds
        serverSelectionTimeoutMS=10000,
    )

    logger.info("Connected to MongoDB")

    # Check for DEV environment
    isprod = not app.config.get("ISDEV", True)

    if isprod == "True":
        logger.info("Connected to PRODUCTION")
        app.ctx.db = client["mitblr-club-api"]
    else:
        logger.info("Connected to DEV ENV")
        app.ctx.db = client["mitblr-club-dev"]


@app.listener("after_server_stop")
async def close_connection(app: Sanic, loop):
    app.ctx.db.close()
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
        d = {"Authenticated": "False", "Message": "No Token"}
        return response.json(d)

    try:
        jwt.decode(request.token, key=request.app.config["PUB_KEY"], algorithms="RS256")
    except jwt.exceptions.ImmatureSignatureError:
        # Raised when a token’s nbf claim represents a time in the future
        d = {
            "Authenticated": "False",
            "Message": "JWT Token not allowed to be used at time",
        }
        status = 401
    except jwt.exceptions.InvalidIssuedAtError:
        # Raised when a token’s iat claim is in the future
        d = {"Authenticated": "False", "Message": "JWT Token issues in future"}
        status = 401
    except jwt.exceptions.ExpiredSignatureError:
        # Raised when a token’s exp claim indicates that it has expired
        d = {"Authenticated": "False", "Message": "JWT Token is expired"}
        status = 401
    except jwt.exceptions.InvalidTokenError:
        # Generic invalid token
        d = {"Authenticated": "False", "Message": "JWT Token invalid"}
        status = 401
    else:
        # Valid Token
        d = {"Authenticated": "True", "Message": "JWT Token is valid"}
        status = 200

    return response.json(d, status=status)


@app.post("/login")
@validate(json=LoginData)
async def login(request: Request, body: LoginData):
    if body.auth_type == "USER":
        user = body.identifier
        password = body.secret

        collection = request.app.ctx.db["authentication"]
        doc = await collection.find_one({"auth_type": "USER", "username": user})
        password_hash = doc["password_hash"]

        if bcrypt.checkpw(password.encode(), password_hash.encode()):
            jwt_dat = {
                "auth_id": str(doc["_id"]),
                "student_id": str(doc["student_id"]),
                "team_id": str(doc["team_id"]),
            }
            jwt = await generate_jwt(app=request.app, data=jwt_dat, validity=90)
            d = {"identifier": jwt, "Authenticated": "True"}
        else:
            d = {"identifier": user, "Authenticated": "False"}

        return response.json(d)

    if body.auth_type == "AUTOMATION":
        app_id = body.identifier
        token = body.secret

        collection = request.app.ctx.db["authentication"]
        doc = await collection.find_one({"auth_type": "AUTOMATION", "app_id": app_id})

        if bcrypt.checkpw(token.encode(), doc["token"].encode()):
            # TODO - Add useful data
            jwt_dat = {"username": app_id}
            jwt = await generate_jwt(app=request.app, data=jwt_dat, validity=1440)
            d = {"identifier": jwt, "Authenticated": "True"}
        else:
            d = {"identifier": app_id, "Authenticated": "False"}

        return response.json(d)


if __name__ == "__main__":
    isdev = app.config.get("ISDEV", True)
    isprod = not isdev
    app.run(debug=isdev, access_log=True, auto_reload=isdev)
