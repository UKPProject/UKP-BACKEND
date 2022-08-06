import random

import aiohttp.web_app
from aiohttp import web

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM
from routes.Discord.citizen.citizen_model import CitizenM
from utils.exceptions import DataNotFilled


class CitizenR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/citizen/account", self.get_citizen),
            web.post("/citizen/account", self.create_citizen),
            web.post("/citizen/work", self.citizen_work),
            web.post("/citizen/job", self.change_job)
        ])
        print("🟡 | Citizen")
    
    async def change_job(self, request: web.Request):
        req_json = await request.json()
        new_job_name = req_json.get("new_job_name")
        citizen_snowflake = req_json.get({"citizen_snowflake"})
        if new_job_name is None:
            return web.json_response({
                "error": "400",
                "ctx": "json",
                "message": "new_job_name not provided in json"
            }, status=400)
        
        db = self.app['db']
        business_found = await db['business'].find_one({"name": str(new_job_name)})
        if business_found is None:
            return web.json_response({
                "error": "400",
                "ctx": "business",
                "message": f"company with that name ({new_job_name}) not found"
            }, status=404)
        
        new_business = await BusinessM(business_found).data()
        citizen = await db['bank'].find_one({"snowflake": str(citizen_snowflake)})
        if citizen is None:
            return web.json_response({
                "error": "400",
                "ctx": "citizen",
                "message": f"citizen with this snowflake ({citizen_snowflake}) not found in db"
            }, status=400)
        
        await db['bank'].update_one(
            {"snowflake": str(citizen_snowflake)},
            {"$set": {"business": str(new_business["name"])}}
        )
        
        return web.json_response({
            "message": "Success!"
        }, status=200)
    
        
    async def citizen_work(self, request: web.Request):
        req_json = await request.json()
        snowflake = req_json.get("snowflake")
        if snowflake is None:
            return web.json_response({"error": "400", "message": "Please provide valid discord ID (snowflake)"},
                                     status=400)

        db = self.app['db']
        
        found_citizen = await db["citizens"].find_one({"snowflake": str(snowflake)})
        if found_citizen is None:
            return web.json_response({"error": "404", "message": "Provided user have no identify in UKP"},
                                     status=404)
        found_bank = await db["bank"].find_one({"snowflake": str(snowflake)})
        if found_bank is None:
            return web.json_response({"error": "409", "message": "Provided user have no bank account in UKP"},
                                     status=409)
        citizen = await CitizenM(found_citizen).data()
        bank_account = await BankM(found_bank).data()
        if bank_account["salary"] == 0.00:
            return web.json_response({"error": "406", "message": "User has no more daily salary"}, status=406)
        
        money = round(random.uniform(0.01, (bank_account["salary"] / 2)), 2)
        await db["bank"].update_one({"snowflake": str(snowflake)}, {"$set": {
            "salary": round((bank_account["salary"] - money), 2)
        }})
        
        return web.json_response({
            "message": "Success!", "reason": f"{citizen['firstName']}, pracowałeś w firmie {bank_account['business']}",
            "money": str(money)
        }, status=200)
        
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
        except DataNotFilled:
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
        