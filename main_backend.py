import asyncio
import motor.motor_asyncio
import aiohttp.web

from routes.Discord.kingdoms.kingdoms_route import KingdomsR

routes = aiohttp.web.RouteTableDef()

if __name__ == "__main__":
    app = aiohttp.web.Application()
    app['db'] = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")['ukp']
    app['db'].get_io_loop = asyncio.get_running_loop
    
    app.add_routes(routes)
    KingdomsR(app)
    aiohttp.web.run_app(app, port=8888)

# yes