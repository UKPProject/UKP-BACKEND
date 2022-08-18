import random
import time

import aiohttp.web_app
from aiohttp import web

from routes.Discord.bank.bank_model import BankM
from routes.Discord.bank.bank_route import log_payment
from routes.Discord.business.business_model import BusinessM, Employee
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
        new_job_salary = req_json.get("new_job_salary")
        citizen_snowflake = req_json.get({"citizen_snowflake"})
        
        if new_job_name is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "json",
                "message": "new_job_name not provided in json"
            }, status=400)
        
        db = self.app['db']
        business_found = await db['business'].find_one({"name": str(new_job_name)})
        
        if business_found is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "business",
                "message": f"company with that name ({new_job_name}) not found"
            }, status=404)
        
        new_business = await BusinessM(business_found).data()
        citizen = await db['bank'].find_one({"snowflake": str(citizen_snowflake)})
        
        if citizen is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "citizen",
                "message": f"citizen with this snowflake ({citizen_snowflake}) not found in db"
            }, status=400)
        
        bank_acc = await db['bank'].find_one({"snowflake": str(citizen_snowflake)})
        bank_m = await BankM(bank_acc).data()
        
        old_business_found = await db['business'].find_one({"name": str(bank_m.get("business"))})
        old_business = await BusinessM(old_business_found).data()
        if new_job_salary is None:
            new_job_salary: float = 0.00
            for employee in old_business.get("employees"):
                if employee.get("snowflake") == citizen_snowflake:
                    new_job_salary = employee.get("salary")
                    break
        
        await db['business'].update_one({"name": str(old_business.get("name"))}, {"$pull": {"employees": {
            "$elemMatch": {"snowflake": str(citizen_snowflake)}
        }}})
        await db['business'].update_one({"name": str(new_business.get("name"))}, {"$push": {"employees": {
            "snowflake": str(bank_m.get('snowflake')),
            "pseo": str(bank_m.get("pseo")),
            "salary": float(new_job_salary),
            "worked": 0
        }}})
        await db['bank'].update_one({"snowflake": str(citizen_snowflake)}, {"$set": {
            "business": str(new_business.get("name")),
            "salary": 0.00
        }})
        
        return web.json_response({
            "status_code": "200",
            "message": "Changed job successfully",
            "ctx": "success"
        }, status=200)
    
    async def citizen_work(self, request: web.Request):
        req_json = await request.json()
        snowflake = req_json.get("snowflake")
        if snowflake is None:
            return web.json_response({"status_code": "400", "message": "Please provide valid discord ID (snowflake)"},
                                     status=400)
        
        db = self.app['db']
        
        found_citizen = await db["citizens"].find_one({"snowflake": str(snowflake)})
        if found_citizen is None:
            return web.json_response({"status_code": "404", "message": "Provided user have no identify in UKP"},
                                     status=404)
        found_bank = await db["bank"].find_one({"snowflake": str(snowflake)})
        if found_bank is None:
            return web.json_response({"status_code": "409", "message": "Provided user have no bank account in UKP"},
                                     status=409)
        citizen = await CitizenM(found_citizen).data()
        bank_account = await BankM(found_bank).data()
        if bank_account["salary"] == 0.00:
            return web.json_response({"status_code": "406", "message": "User has no more daily salary"}, status=406)
        
        money = round(random.uniform(0.01, (bank_account["salary"] / 2)), 2)
        
        await db["bank"].update_one({"snowflake": str(snowflake)}, {"$inc": {"salary": -money}})
        await db["bank"].update_one({"snowflake": str(snowflake)}, {"$inc": {"money": money}})
        
        await log_payment(db, {
            "sender": str(bank_account.get("business")),
            "receiver": str(snowflake),
            "money": float(money),
            "timestamp": str(int(time.time())),
            "method": "plus" if float(money) >= 0.00 else "minus",
            "reason": "salary"
        })
        
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": f"{citizen['firstName']}, pracowałeś w firmie {bank_account['business']}",
            "extra": {"money": str(money)}
        }, status=200)
    
    async def get_citizen(self, request: web.Request):
        req_headers = request.headers
        pseo = req_headers.get("pseo")
        snowflake = req_headers.get("snowflake")
        if pseo is None and snowflake is None:
            return web.json_response(
                {"status_code": "400", "message": "Please provide valid PSEO or discord ID (snowflake)"},
                status=400)
        if pseo is None:
            found = await self.app['db']["citizens"].find_one({"snowflake": str(snowflake)})
            if found is None:
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                           "snowflake)"}, status=400)
            citizen = await CitizenM(found).data()
            return web.json_response(citizen, status=200)
        elif snowflake is None:
            found = await self.app['db']["citizens"].find_one({"pseo": str(pseo)})
            if found is None:
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                           "snowflake)"}, status=400)
            citizen = await CitizenM(found).data()
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": citizen
            }, status=200)
    
    async def create_citizen(self, request: web.Request):
        req_json = await request.json()
        try:
            CitizenM(req_json)
        except DataNotFilled:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide all needed values in your request json"
            }, status=400)
        new_citizen = await CitizenM(req_json).data()
        found_check = await self.app['db']["citizens"].find_one({"snowflake": str(new_citizen["snowflake"])})
        if found_check is None:
            await self.app['db']["citizens"].insert_one(new_citizen)
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": "Citizen created successfully"
            }, status=200)
        else:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": "User with this discord ID already registered"
            }, status=400)
