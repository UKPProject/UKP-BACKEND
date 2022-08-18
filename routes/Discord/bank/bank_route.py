import time
from typing import TypedDict

import aiohttp.web_app
from aiohttp import web

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM
from routes.Discord.citizen.citizen_model import CitizenM
from utils.exceptions import DataNotFilled


class PaymentCtx(TypedDict):
    reason: str
    money: float
    sender: str
    receiver: str
    timestamp: str
    method: str
    

async def log_payment(db, ctx: PaymentCtx):
    await db["bank_logs"].insert_one(ctx)


class BankR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/bank/account", self.get_bank_account),
            web.post("/bank/account", self.create_bank_account)
        ])
        print("🟡 | Bank")
    
    async def send_money(self, request: web.Request):
        req_json = await request.json()
        from_snowflake = req_json.get("from_snowflake")
        to_snowflake = req_json.get("to_snowflake")
        money = req_json.get("money")
        reason = req_json.get("reason")
        
        db = self.app["db"]
        
        citizen_to = await db["citizens"].find_one({"snowflake": str(to_snowflake)})
        if citizen_to is None:
            return web.json_response({"status_code": "400", "ctx": "not_found", "message": "Citizen (to) not registered in UKP system"},
                                     status=404)
        citizen_from = await db["bank"].find_one({"snowflake": str(from_snowflake)})
        c_from = await BankM(citizen_from).data()
        
        if c_from["balance"] < float(money):
            return web.json_response({"status_code": "400", "ctx": "not_enough", "message": "Citizen don't have enough money"}, status=409)
        
        await db["bank"].update_one({"snowflake": str(from_snowflake)}, {"$inc": {"balance": -float(money)}})
        await db["bank"].update_one({"snowflake": str(to_snowflake)}, {"$inc": {"balance": float(money)}})
        await log_payment(db, {
            "sender": str(from_snowflake),
            "receiver": str(to_snowflake),
            "money": float(money),
            "timestamp": str(int(time.time())),
            "method": "plus" if float(money) >= 0.00 else "minus",
            "reason": str(reason)
        })
        return web.json_response({"status_code": "200", "ctx": "success", "message": "Money sent successfully"}, status=200)
    
    async def get_bank_account(self, request: web.Request):
        req_headers = request.headers
        pseo = req_headers.get("pseo")
        snowflake = req_headers.get("snowflake")
        if pseo is None and snowflake is None:
            return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID (snowflake)"},
                                     status=400)
        if pseo is None:
            found = await self.app['db']["bank"].find_one({"snowflake": str(snowflake)})
            if found is None:
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            bank_account = await CitizenM(found).data()
            return web.json_response(bank_account, status=200)
        elif snowflake is None:
            found = await self.app['db']["bank"].find_one({"pseo": str(pseo)})
            if found is None:
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                     "snowflake)"}, status=400)
            bank_account = await CitizenM(found).data()
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": bank_account
            }, status=200)
    
    async def create_bank_account(self, request: web.Request):
        req_json = await request.json()
        
        try:
            await BankM(req_json).data()
        except DataNotFilled:
            return web.json_response({
                "status_code": "400",
                "message": "Please fill all data in your request json"
            }, status=400)
        
        db = self.app['db']
        data = await BankM(req_json).data()
        
        found = await db["bank"].find_one({"pseo": str(data.get("pseo")), "snowflake": str(data.get("snowflake"))})
        if found is not None:
            return web.json_response({
                "status_code": "409",
                "message": "Account of that user already exists"
            }, status=409)
        
        found_business = await db["businesses"].find_one({"name": str(data.get("business"))})
        if found_business is None:
            return web.json_response({
                "status_code": "404",
                "message": "Business with that name not found"
            }, status=404)
        
        await db["bank"].insert_one(data)
        await db["businesses"].update_one({"name": str(data.get("business"))}, {"$push": {"employees": {
            "snowflake": str(data.get("snowflake")),
            "salary": float(data.get("salary")),
            "pseo": str(data.get("pseo")),
            "worked": 0
        }}})
        
        return web.json_response({"message": "Citizen created successfully", "status_code": "200", "ctx": "success"}, status=200)
