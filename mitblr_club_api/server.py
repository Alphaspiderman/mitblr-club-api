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

@app.get("/")
async def get_root(request: Request):
    return response.text("Pong")


if __name__ == "__main__":
    app.run(debug=True, access_log=True, auto_reload=True)
    logger.info("Test")
