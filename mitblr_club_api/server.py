from sanic import Sanic
from sanic.log import logger
import motor.motor_asyncio as async_motor
from dotenv import dotenv_values

from sanic.views import HTTPMethodView
from sanic import response, Request

from app import appserver

logger.debug("Loading ENV")
config = dotenv_values(".env")

app = appserver

import clubs, students

app.config.update(config)

@app.listener("before_server_start")
async def register_db(app: Sanic):
    logger.info("Connnecting to MongoDB")
    # Create a database connection pool
    app.ctx.db = async_motor.AsyncIOMotorClient(
        app.config["MONGO_CONNECTION_URI"],
        # in milliseconds
        maxIdleTimeMS=10000,
        # minimal pool size
        minPoolSize=10,
        # maximal pool size
        maxPoolSize=50,
        # connection timeout in miliseconds
        connectTimeoutMS=10000,
        # boolean
        retryWrites=True,
        # wait queue in miliseconds
        waitQueueTimeoutMS=10000,
        # in miliseconds
        serverSelectionTimeoutMS=10000,
    )
    logger.info("Connnected to MongoDB")


@app.listener("after_server_stop")
async def close_connection(app, loop):
    app.ctx.db.close()
    logger.info("Disconnected from MongoDB")

@app.get("/")
async def get_root(request: Request):
    return response.text("Pong")


if __name__ == "__main__":
    app.run(debug=True, access_log=True, auto_reload=True)
    logger.info("Test")
