import datetime
from json import JSONDecodeError
from typing import Optional, TypedDict

import aiohttp.web
import aiohttp.web_exceptions
from aiohttp import web
from colorama import Fore
import aiofiles

class DataNotFilled(Exception):
    pass

class ConnectionWS(TypedDict):
    connection_id: str
    token: str
    ws: web.WebSocketResponse

async def log(request: Optional[aiohttp.web.Request] = None, status: Optional[int] = None, custom_message: Optional[str] = None):
    if request:
        color: str
        if str(status).startswith("2"):
            color = Fore.GREEN
        elif str(status).startswith("4"):
            color = Fore.LIGHTYELLOW_EX
        elif str(status).startswith("5"):
            color = Fore.RED
        else:
            color = Fore.MAGENTA
            
        path = request.path.replace("/", "", 1).replace("/", ".").upper()
        async with aiofiles.open("./backendlogs.txt", "a") as out:
            await out.write(f"[{status}] | {request.method.upper()} | {datetime.datetime.now()} | {path}"+"\n")
            await out.flush()
        print(f"{color}[{status}]{Fore.RESET} | {request.method.upper()} | {datetime.datetime.now()} | {color}{path}{Fore.RESET}")
    else:
        async with aiofiles.open("./backendlogs.txt", "a") as out:
            await out.write(custom_message.replace("[39m", "").replace("[92m", "").replace("[35m", "") +"\n")
            await out.flush()
        print(custom_message)