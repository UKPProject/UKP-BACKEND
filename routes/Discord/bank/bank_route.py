import asyncio
import time
import uuid
from typing import TypedDict, Union, List

import aiohttp.web_app
from aiohttp import web, WSMsgType
from colorama import Fore

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM
from tools.miscellaneous import DataNotFilled, log


class PaymentCtx(TypedDict):
    reason: str
    money: int
    sender: str
    receiver: str
    timestamp: str
    method: str
    token: str
    authorized: bool


async def log_payment(db, ctx: PaymentCtx):
    await db["bank_logs"].insert_one(ctx)


class BankR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/bank/account", self.get_bank_account),
            web.post("/bank/account", self.create_bank_account),
            web.post("/bank/transaction", self.send_money),
            web.get("/bank/websocket", self.bank_websocket),
            web.get("/bank/account/all", self.get_all_accounts)
        ])
        self.bot_websocket: Union[web.WebSocketResponse, None] = None
        self.pending_transactions: List[PaymentCtx] = []
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| Bank")
    
    async def get_all_accounts(self, request: web.Request):
        req_headers = request.headers
        kingdom = req_headers.get("kingdom")
        if kingdom is None:
            db = self.app['db']
            return web.json_response([await BankM(account).data() async for account in db["bank"].find()], status=200)
        else:
            db = self.app['db']
            return web.json_response(
                [await BankM(account).data() async for account in db["bank"].find({"kingdom": kingdom.lower()})],
                status=200)
    
    async def bank_websocket(self, request: web.Request):
        print("sasa")
        if self.bot_websocket is None:
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            while True:
                msg = await ws.receive()
                if msg.type == WSMsgType.TEXT:
                    data: dict = msg.json()
                    match data.get("action"):
                        case "authorize":
                            if data.get("value") == "BOT_WEBSOCKET":
                                await ws.send_json({
                                    "message": "success! Added you to list",
                                    "action": "token_auth_granted"
                                })
                                self.bot_websocket = ws
                        case "transaction_auth_granted":
                            for transaction in self.pending_transactions:
                                if transaction.get("token") == data.get("token"):
                                    transaction["authorized"] = True
                                    break
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED, WSMsgType.ERROR):
                    self.bot_websocket = None
                    for transaction in self.pending_transactions:
                        transaction["authorized"] = False
                await asyncio.sleep(0)
    
    async def send_money(self, request: web.Request):
        req_json = await request.json()
        from_snowflake = req_json.get("from_snowflake")
        to_snowflake = req_json.get("to_snowflake")
        money = req_json.get("money")
        reason = req_json.get("reason")
        transaction_token = str(uuid.uuid4())
        
        db = self.app["db"]
        if from_snowflake.startswith("b+"):
            citizen_from = await db["business"].find_one({"businessId": str(from_snowflake)})
            if citizen_from is None:
                await log(request, 400)
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": "Business (from) has not been found in database. Make sure you entered right ID"
                }, status=400)
            c_from = await BusinessM(citizen_from).data()
            
            if c_from["money"] < int(money):
                await log(request, 409)
                return web.json_response(
                    {"status_code": "409", "ctx": "not_enough", "message": "Citizen don't have enough money"},
                    status=409)
            await db["business"].update_one({"businessId": str(from_snowflake)}, {"$inc": {"money": -int(money)}})
        elif from_snowflake.startswith("b+") is False:
            citizen_from = await db["bank"].find_one({"snowflake": str(from_snowflake)})
            if citizen_from is None:
                await log(request, 400)
                return web.json_response(
                    {"status_code": "400", "ctx": "not_found",
                     "message": "Citizen (from) not registered in UKP system"},
                    status=400)
            c_from = await BankM(citizen_from).data()
            
            if c_from["balance"] < int(money):
                await log(request, 409)
                return web.json_response(
                    {"status_code": "409", "ctx": "not_enough", "message": "Citizen don't have enough money"},
                    status=409)
            
            await self.bot_websocket.send_json({
                "action": "transaction_request",
                "from": from_snowflake,
                "to": to_snowflake,
                "money": money,
                "reason": reason,
                "token": transaction_token
            })
            self.pending_transactions.append({
                "sender": str(from_snowflake),
                "receiver": str(to_snowflake),
                "money": int(money),
                "timestamp": str(int(time.time())),
                "method": "plus" if int(money) >= 0.00 else "minus",
                "reason": str(reason),
                "token": transaction_token,
                "authorized": False
            })
            start_time = time.time()
            while True:
                if int(time.time() - start_time) >= 25:
                    return web.json_response({
                        "status_code": "401",
                        "ctx": "auth_timeout",
                        "message": "user has not authorized the transaction in time or refused it"
                    }, status=401)
                transaction_ctx = \
                list(filter(lambda x: x.get("token") == transaction_token, self.pending_transactions))[0]
                if transaction_ctx["authorized"] is True:
                    await db["bank"].update_one({"snowflake": str(from_snowflake)}, {"$inc": {"balance": -int(money)}})
                    self.pending_transactions.remove(transaction_ctx)
                    break
                await asyncio.sleep(0)
        
        if to_snowflake.startswith("b+"):
            citizen_to = await db["business"].find_one({"businessId": str(to_snowflake)})
            if citizen_to is None:
                await log(request, 400)
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": "Business (from) has not been found in database. Make sure you entered right ID"
                }, status=400)
            
            await db["business"].update_one({"businessId": str(to_snowflake)}, {"$inc": {"money": int(money)}})
        elif to_snowflake.startswith("b+") is False:
            citizen_to = await db["citizens"].find_one({"snowflake": str(to_snowflake)})
            if citizen_to is None:
                await log(request, 400)
                return web.json_response(
                    {"status_code": "400", "ctx": "not_found", "message": "Citizen (to) not registered in UKP system"},
                    status=400)
            
            await db["bank"].update_one({"snowflake": str(to_snowflake)}, {"$inc": {"balance": int(money)}})
        
        await log_payment(db, {
            "sender": str(from_snowflake),
            "receiver": str(to_snowflake),
            "money": int(money),
            "timestamp": str(int(time.time())),
            "method": "plus" if int(money) >= 0.00 else "minus",
            "reason": str(reason),
            "token": transaction_token,
            "authorized": True
        })
        await log(request, 200)
        return web.json_response({"status_code": "200", "ctx": "success", "message": "Money sent successfully"},
                                 status=200)
    
    async def get_bank_account(self, request: web.Request):
        req_headers = request.headers
        pseo = req_headers.get("pseo")
        snowflake = req_headers.get("snowflake")
        if pseo is None and snowflake is None:
            await log(request, 400)
            return web.json_response(
                {"status_code": "400", "message": "Please provide valid PSEO or discord ID (snowflake)"},
                status=400)
        if pseo is None:
            found = await self.app['db']["bank"].find_one({"snowflake": str(snowflake)})
            if found is None:
                await log(request, 400)
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                           "snowflake)"}, status=400)
            bank_account = await BankM(found).data()
            await log(request, 200)
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": bank_account
            }, status=200)
        elif snowflake is None:
            found = await self.app['db']["bank"].find_one({"pseo": str(pseo)})
            if found is None:
                await log(request, 400)
                return web.json_response({"status_code": "400", "message": "Please provide valid PSEO or discord ID ("
                                                                           "snowflake)"}, status=400)
            bank_account = await BankM(found).data()
            await log(request, 200)
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

        """
        found_business = await db["business"].find_one({"businessId": str(data.get("businessId"))})
        if found_business is None:
            return web.json_response({
                "status_code": "404",
                "message": "Business with that id not found"
            }, status=404)
        
        
        await db["business"].update_one({"businessId": str(data.get("businessId"))}, {"$push": {"employees": {
            "snowflake": str(data.get("snowflake")),
            "salary": int(data.get("salary")),
            "pseo": str(data.get("pseo")),
            "worked": 0
        }}})
        """
        await db["bank"].insert_one(data)
        return web.json_response({"message": "Bank account created successfully", "status_code": "200", "ctx": "success"},
                                 status=200)
