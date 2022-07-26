import aiohttp.web_app
from aiohttp import web

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM
from routes.Discord.citizen.citizen_model import CitizenM
from utils.exceptions import DataNotFilled


class KingdomsR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/bank/account", self.get_bank_account),
            web.post("/bank/account", self.create_bank_account)
        ])
        
    async def get_bank_account(self, request: web.Request):
        req_headers = request.headers
        pseo = req_headers.get("pseo")
        snowflake = req_headers.get("snowflake")
        if pseo is None and snowflake is None:
            return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID (snowflake)"},
                                     status=400)
        if pseo is None:
            found = await self.app['db']["bank"].find_one({"snowflake": str(snowflake)})
            if found is None:
                return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            bank_account = await CitizenM(found).data()
            return web.json_response(bank_account, status=200)
        elif snowflake is None:
            found = await self.app['db']["bank"].find_one({"pseo": str(pseo)})
            if found is None:
                return web.json_response({"error": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            bank_account = await CitizenM(found).data()
            return web.json_response(bank_account, status=200)
        
    async def create_bank_account(self, request: web.Request):
        req_json = await request.json()
        
        try:
            await BankM(req_json).data()
        except DataNotFilled:
            return web.json_response({
                "error": "400",
                "message": "Please fill all data in your request json"
            }, status=400)
        
        db = self.app['db']
        data = await BankM(req_json).data()
        
        found = await db["bank"].find_one({"pseo": str(data.get("pseo")), "snowflake": str(data.get("snowflake"))})
        if found is not None:
            return web.json_response({
                "error": "409",
                "message": "Account of that user already exists"
            }, status=409)
        
        found_business = await db["businesses"].find_one({"name": str(data.get("business"))})
        if found_business is None:
            return web.json_response({
                "error": "404",
                "message": "Business with that name not found"
            }, status=404)
        
        business = await BusinessM(found_business).data()
        employees = business.get("employees")
        employees.append({
            "snowflake": str(data.get("snowflake")),
            "salary": float(data.get("salary")),
            "pseo": str(data.get("pseo"))
        })
        
        await db["bank"].insert_one(data)
        await db["businesses"].update_one({"name": str(data.get("business"))}, {"$set": {"employees": employees}})
        
        return web.json_response({"message": "Success!"}, status=200)
        