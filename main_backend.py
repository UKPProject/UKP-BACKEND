"""
import asyncio
import time

import motor.motor_asyncio
import aiohttp.web

from routes.Discord.bank.bank_route import BankR
from routes.Discord.citizen.citizen_route import CitizenR
from routes.Discord.kingdoms.kingdoms_route import KingdomsR
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
    UpdateSalary(app)
    print(f"🟢 | Running up {time.localtime().tm_hour}:{time.localtime().tm_min}")
    aiohttp.web.run_app(app, port=8888)
"""

import time

import aiohttp
import asyncio
import threading


cookies = {
    "cf_clearance": ".Rsda2GSFyT3FucMqACZjI_O2smBPCJi3uhFSUVWPjo-1659453045-0-150"
}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.77"
}

async def repeat(interval, func, *args, **kwargs):
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval),
        )


async def getting():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://advicebot.info/", cookies=cookies, headers=headers) as req:
            print(f"{req.status}, {time.time()}")


if __name__ == '__main__':
    async def main():
        threads = []
        for x in range(5):
            t = threading.Thread(target=asyncio.run, args=(repeat(0, getting), ))
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()
    
    
    asyncio.run(main())