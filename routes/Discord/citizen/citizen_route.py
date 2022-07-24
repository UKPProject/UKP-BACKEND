import aiohttp.web_app
from aiohttp import web

from routes.Discord.citizen.citizen_model import CitizenM


class CitizenR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/citizen/account", self.get_citizen),
            web.post("/citizen/account", self.create_citizen)
        ])
    
    async def get_citizen(self, request: web.Request):
        req_headers = request.headers
        pseo = req_headers.get("pseo")
        snowflake = req_headers.get("snowflake")
        if pseo is None and snowflake is None:
            return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID (snowflake)"},
                                     status=400)
        if pseo is None:
            found = await self.app['db']["citizens"].find_one({"snowflake": str(snowflake)})
            if found is None:
                return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            citizen = await CitizenM(found).data()
            return web.json_response(citizen, status=200)
        elif snowflake is None:
            found = await self.app['db']["citizens"].find_one({"pseo": str(pseo)})
            if found is None:
                return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            citizen = await CitizenM(found).data()
            return web.json_response(citizen, status=200)
            
    async def create_citizen(self, request: web.Request):
        req_json = await request.json()
        try:
            CitizenM(req_json)
        except TypeError:
            return web.json_response({
                "error": "400", "message": "Please provide all needed values in your request json"
            }, status=400)
        new_citizen = await CitizenM(req_json).data()
        found_check = await self.app['db']["citizens"].find_one({"snowflake": str(new_citizen["snowflake"])})
        if found_check is None:
            await self.app['db']["citizens"].insert_one(new_citizen)
            return web.json_response({"message": "Success!"}, status=200)
        else:
            return web.json_response({"error": "400", "message": "User with this discord ID already registered"}, status=200)

        # yes