import asyncio
from secrets import token_urlsafe
from typing import List

import aiohttp.web_app
from aiohttp import web, WSMsgType
from colorama import Fore

from tools.miscellaneous import ConnectionWS


class MinecraftChatPortal:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/minecraft/chat/ws", self.websocket_handler)
        ])
        self.authorized_connections = []
        self.authorized_tokens = ["PLUGIN_WEBSOCKET", "BOT_WEBSOCKET"]
        self.used_tokens: List[ConnectionWS] = []
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| MinecraftChatPortal")
    
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
                                self.used_tokens.append(
                                    {"connection_id": str(connection_id), "token": str(data.get("value")), "ws": ws})
                                await ws.send_json(
                                    {"message": "success! Added you to list", "action": "token_auth_granted"})
                        else:
                            await ws.send_json(
                                {"error": "invalid token. Please provide valid token", "action": "token_auth_declined"})
                            break
    
                    case "player_join_server_minecraft":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "BOT_WEBSOCKET":
                                await ws_conn.get("ws").send_json(
                                    {"action": "player_join_server", "data": data.get('data')})
                                
                    case "player_left_server_minecraft":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "BOT_WEBSOCKET":
                                await ws_conn.get("ws").send_json(
                                    {"action": "player_left_server", "data": data.get('data')})
                                
                    case "send_message_discord":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "PLUGIN_WEBSOCKET":
                                await ws_conn.get("ws").send_json({"action": "new_incoming_message_discord", "data": data.get('data')})  # data = {"player_message_content": "treść wiadomości", "player_nick": "Krzychu#4788", "player_d_id": "698239897755975960"}
                    case "send_message_minecraft":
                        for ws_conn in self.used_tokens:
                            if ws_conn.get("token") == "BOT_WEBSOCKET":
                                await ws_conn.get("ws").send_json({"action": "new_incoming_message_minecraft", "data": data.get('data')})  # data = {"player_message_content": "treść wiadomości", "player_nick": "Krzychu1289", "player_d_id": "698239897755975960", "featured_kingdom": "USE"}
        
            elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
                if connection_id in self.authorized_connections:
                    self.authorized_connections.remove(connection_id)
                    for used_token in self.used_tokens:
                        if used_token.get("connection_id") == connection_id:
                            self.used_tokens.remove(used_token)
                await ws.close()
                break
            await asyncio.sleep(0)
        