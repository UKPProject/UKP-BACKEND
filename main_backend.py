import asyncio

import aiohttp_cors
import time

import motor.motor_asyncio
import aiohttp.web
from colorama import Fore

from routes.Dashboard.oauth_route import OAuthR
from routes.Discord.bank.bank_route import BankR
from routes.Discord.citizen.citizen_route import CitizenR
from routes.Discord.kingdoms.kingdoms_route import KingdomsR
from routes.Discord.rates.rates_route import RatesR
from utils.background_tasks import UpdateSalary

routes = aiohttp.web.RouteTableDef()

if __name__ == "__main__":
    app = aiohttp.web.Application()
    
    app['db'] = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")['ukp']
    app['db'].get_io_loop = asyncio.get_running_loop
    
    app.add_routes(routes)
    KingdomsR(app)
    CitizenR(app)
    BankR(app)
    RatesR(app)
    OAuthR(app)
    UpdateSalary(app)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })
    
    for route in list(app.router.routes()):
        cors.add(route)
    print(f"{Fore.LIGHTGREEN_EX}[RUN]{Fore.RESET} | Running up {time.localtime().tm_hour}:{time.localtime().tm_min}")
    aiohttp.web.run_app(app, port=8888, host="localhost")