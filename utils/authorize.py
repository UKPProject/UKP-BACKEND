import asyncio
from functools import wraps
import urllib.parse
from quart import request

AUTHORIZATION_TOKENS = {
    0: [urllib.parse.quote("T4mDdPdZZkvzEDQR"), urllib.parse.quote("wHP39m6XVZBpft2f")],
    1: [urllib.parse.quote("yWE8aWnE*C=!xYp#TR6M"), urllib.parse.quote("ZYUE7W^nt=afFwaGNWea")]
}


def authorize(authorization_level: int):
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            authorization_token = request.headers.get("Authorization")
            if authorization_token is not None:
                if urllib.parse.quote(authorization_token) not in AUTHORIZATION_TOKENS[authorization_level]:
                    return {
                        'code': 401,
                        'message': "Invalid authorization token provided"
                    }, 401
            else:
                return {
                    'code': 401,
                    'message': "Please provide a valid authorization token in headers"
                               " e.g. {Authorization: Valid_authorization_token}"
                }, 401
            return await f()
        return decorated_function
    return decorator
