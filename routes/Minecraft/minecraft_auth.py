from typing import TypedDict, List

import aiohttp.web_app
from aiohttp import web, WSMsgType
from colorama import Fore
from secrets import token_urlsafe

from tools.miscellaneous import DataNotFilled, ConnectionWS, log


class PlayerDB(TypedDict):
    uuid: str
    d_id: str
    id: str
    timestamp: str
    
class PlayerDBModel:
    def __init__(self, cursor: dict):
        try:
            self._uuid: str = str(cursor.get("uuid"))
            self._d_id: str = str(cursor.get("d_id"))
            self._timestamp: int = int(cursor.get("timestamp"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> PlayerDB:
        return {
            "uuid": str(self._uuid),
            "d_id": str(self._d_id),
            "id": str(self._d_id),
            "timestamp": str(self._timestamp),
        }
    
class MinecraftAuthAPI:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/minecraft/auth/ws", self.websocket_handler),
            web.get("/minecraft/auth", self.check_player_authorized),
            web.get("/minecraft/auth/guild", self.get_usernames_in_guild)
        ])
        self.authorized_connections = []
        self.authorized_tokens = ["PLUGIN_WEBSOCKET", "BOT_WEBSOCKET"]
        self.used_tokens: List[ConnectionWS] = []
        self.usernames_in_ukp: List[str] = []
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| MinecraftAuthorizationAPI")

    async def get_usernames_in_guild(self, request: web.Request):
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": self.usernames_in_ukp
        }, status=200)

    async def check_player_authorized(self, request: web.Request):
        req_headers = request.headers
        print(req_headers)
        await log(request, 699)
        if req_headers.get("uuid"):
            db = self.app["db"]['minecraft_auth']
            found = await db.find_one({"uuid": str(req_headers.get("uuid"))})
            if found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": "user not found in db"
                }, status=400)
            data = await PlayerDBModel(found).data()
            await log(request, 200)
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": data
            }, status=200, headers={"d_id": data.get("d_id")})
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "not_found",
                "message": "uuid not found in headers"
            }, status=400)
    
    async def websocket_handler(self, request: web.Request):
        ws = web.WebSocketResponse()
        connection_id = token_urlsafe(12)
        await ws.prepare(request)
        while True:
            msg = await ws.receive()
            if msg.type == WSMsgType.TEXT:
                print(msg)
                data: dict = msg.json()
                match data.get("action"):
                    case "authorize":
                        if data.get("value") in self.authorized_tokens:
                            for obj in self.used_tokens:
                                if obj.get("token") == data.get("value"):
                                    await ws.send_json({"error": "token already in use"})
                                    break
                            else:
                                self.authorized_connections.append(connection_id)
                                self.used_tokens.append({"connection_id": str(connection_id), "token": str(data.get("value")), "ws": ws})
                                await ws.send_json({"message": "success! Added you to list", "action": "token_auth_granted"})
                        else:
                            await ws.send_json({"error": "invalid token. Please provide valid token", "action": "token_auth_declined"})
                            break
                    case "login_minecraft":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "BOT_WEBSOCKET":
                                await ws_conn.get("ws").send_json({"action": "authorization_need", "data": data.get("player_data")}) # data = {"ip": "ip player", "uuid": "uuid", "player_nick": "player_nick_from_mc", "requested_id": "id", "timestamp": "timestamp"}
                    case "authorization_login_granted":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "PLUGIN_WEBSOCKET":
                                await ws_conn.get("ws").send_json({"action": "authorization_granted", "data": data.get("data")})
                                if data.get("remember_me") == "1": # 1 = True 0 = False
                                    db = self.app["db"]
                                    data = data.get("data")
                                    discord_id = str(data.get("requested_id"))
                                    uuid = str(data.get("uuid"))
                                    timestamp = str(data.get("timestamp"))
                                    print(data)
                                    found_mc = await db['minecraft_auth'].find_one({"uuid": uuid})
                                    if found_mc is None:
                                        found_discord = await db['minecraft_auth'].find_one({"d_id": discord_id})
                                        if found_discord is None:
                                            await db['minecraft_auth'].insert_one({"uuid": uuid, "d_id": discord_id, "timestamp": timestamp})
                                        else:
                                            await db['minecraft_auth'].update_one({"d_id": discord_id}, {"$set": {"uuid": uuid, "timestamp": timestamp}})
                                    else:
                                        await db['minecraft_auth'].update_one({"uuid": uuid}, {"$set": {"d_id": discord_id, "timestamp": timestamp}})
   
                    case "update_usernames":
                        self.usernames_in_ukp = data.get("usernames")
                                    
                    case "authorization_login_denied":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "PLUGIN_WEBSOCKET":
                                await ws_conn.get("ws").send_json({"action": "authorization_denied"})
                            
            elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
                if connection_id in self.authorized_connections:
                    self.authorized_connections.remove(connection_id)
                    for used_token in self.used_tokens:
                        if used_token.get("connection_id") == connection_id:
                            self.used_tokens.remove(used_token)
                await ws.close()
                break