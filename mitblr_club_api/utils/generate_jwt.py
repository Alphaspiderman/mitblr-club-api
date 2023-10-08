from sanic import Sanic
from datetime import timedelta, datetime
import jwt


async def generate_jwt(app: Sanic, data: dict, validity: int):
    """Generates JWT with given data"""
    expire = datetime.utcnow() + timedelta(minutes=validity)
    data.update({"exp": expire})
    return jwt.encode(data, app.config["PRIV_KEY"], algorithm="RS256")
