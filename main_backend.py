import asyncio
import threading

import aiohttp_cors
import time

from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp.web
from colorama import Fore

from routes.Dashboard.oauth.oauth_route import OAuthR
from routes.Discord.bank.bank_route import BankR
from routes.Discord.business.business_route import BusinessR
from routes.Discord.citizen.citizen_route import CitizenR
from routes.Discord.kingdoms.kingdoms_route import KingdomsR
from routes.Discord.rates.rates_route import RatesR
from routes.Minecraft.minecraft_auth import MinecraftAuthAPI
from routes.Minecraft.minecraft_chat_portal import MinecraftChatPortal
from routes.Minecraft.minecraft_job_block import MinecraftJobBlock
from tools.background_tasks import UpdateSalary
from tools.miscellaneous import log

routes = aiohttp.web.RouteTableDef()

if __name__ == "__main__":
    app = aiohttp.web.Application()
    
    #app['db'] = AsyncIOMotorClient("mongodb://158.101.119.184:1541")['ukp']
    app['db'] = AsyncIOMotorClient("mongodb://localhost:1541")['ukp']
    app['db'].get_io_loop = asyncio.get_running_loop
    
    app.add_routes(routes)
    KingdomsR(app)
    BusinessR(app)
    CitizenR(app)
    BankR(app)
    RatesR(app)
    OAuthR(app)
    UpdateSalary(app)
    MinecraftAuthAPI(app)
    MinecraftChatPortal(app)
    MinecraftJobBlock(app)
    
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
        
    asyncio.run(log(custom_message=f"{Fore.LIGHTGREEN_EX}[RUN]{Fore.RESET} | Running up {time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year} | {time.localtime().tm_hour}:{time.localtime().tm_min}"))
    aiohttp.web.run_app(app, port=9126, host="0.0.0.0")