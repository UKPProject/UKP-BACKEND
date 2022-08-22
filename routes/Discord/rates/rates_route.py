import aiohttp.web_app
from aiohttp import web
from colorama import Fore

from routes.Discord.rates.rates_model import RatesM
from utils.exceptions import DataNotFilled


class RatesR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.post("/rates", self.create_rate),
            web.get("/rates", self.get_rate),
            web.put("/rates", self.update_rate)
        ])
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| Rates")
    
    async def update_rate(self, request: web.Request):
        req_json = await request.json()
        name = req_json.get("name")
        code = req_json.get("code")
        new_value = req_json.get("value")
        if name is None and code is None and new_value is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid name or code"
            }, status=400)
        if name is None:
            found = await self.app['db']["rates"].find_one({"code": str(code)})
            if found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "data",
                    "message": "Please provide valid name or code"
                }, status=400)
            rate = await RatesM(found).data()
            await self.app['db']["rates"].update_one({"code": str(code)}, {"$push": {"oldValues": rate.get("value")}})
            await self.app['db']["rates"].update_one({"code": str(code)}, {"$set": {"value": float(new_value)}})
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": "Rate updated",
            }, status=200)
        
        elif code is None:
            found = await self.app['db']["rates"].find_one({"name": str(name)})
            if found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "data",
                    "message": "Please provide valid name or code"
                }, status=400)
            rate = await RatesM(found).data()
            await self.app['db']["rates"].update_one({"name": str(name)}, {"$push": {"oldValues": rate.get("value")}})
            await self.app['db']["rates"].update_one({"name": str(name)}, {"$set": {"value": float(new_value)}})
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": "Rate updated",
            }, status=200)
        
    async def create_rate(self, request: web.Request):
        req_json = await request.json()
        try:
            await RatesM(req_json).data()
        except DataNotFilled:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please fill up all necessary data"
            }, status=400)
        db = self.app['db']["rates"]
        data = await RatesM(req_json).data()
        found = await db.find_one({"name": str(data.get("name"))})
        if found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": "Rate with this name already exists"
            }, status=400)
        found = await db.find_one({"code": str(data.get("code"))})
        if found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": "Rate with this code already exists"
            }, status=400)
        
        await db.insert_one(data)
        return web.json_response({"status_code": "200", "ctx": "success", "message": "Rate created"}, status=200)
    
    async def get_rate(self, request: web.Request):
        req_headers = request.headers
        name = req_headers.get("name")
        code = req_headers.get("code")
        if name is None and code is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid name or code"
            }, status=400)
        if name is None:
            found = await self.app['db']["rates"].find_one({"code": str(code)})
            if found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "data",
                    "message": "Please provide valid name or code"
                }, status=400)
            rate = await RatesM(found).data()
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": rate,
            }, status=200)
        elif code is None:
            found = await self.app['db']["rates"].find_one({"name": str(name)})
            if found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "data",
                    "message": "Please provide valid name or code"
                }, status=400)
            rate = await RatesM(found).data()
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": rate,
            }, status=200)
        