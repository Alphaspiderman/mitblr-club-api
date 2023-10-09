import bcrypt
import motor.motor_asyncio as async_motor
from dotenv import dotenv_values
from sanic import Request, Sanic, response
from sanic.log import logger
from sanic_ext import validate

from .app import appserver
from .models.login_data import LoginData
from .utils.generate_jwt import generate_jwt

# flake8: noqa

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


@app.post("/login")
@validate(json=LoginData)
async def login(request: Request, body: LoginData):
    body = body.model_dump()
    if body["auth_type"] == "USER":
        user = body["identifier"]
        passwd = body["secret"]

        collection = request.app.ctx.db["authentication"]
        doc = await collection.find_one({"auth_type": "USER", "username": user})

        if bcrypt.checkpw(passwd.encode(), doc["passwd_hash"].encode()):
            # TODO - Add useful data
            jwt_dat = {"username": user}
            jwt = await generate_jwt(app=request.app, data=jwt_dat, validity=60)
            d = {"identifier": jwt, "Authenticated": "True"}
        else:
            d = {"identifier": user, "Authenticated": "False"}

        return response.json(d)

    if body["auth_type"] == "AUTOMATION":
        app_id = body["identifier"]
        token = body["secret"]

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
