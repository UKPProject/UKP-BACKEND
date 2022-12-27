import aiohttp.web_app
from aiohttp import web
from colorama import Fore

import os
from dotenv import load_dotenv

load_dotenv()


class OAuthR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.post("/oauth/callback", self.oauth_callback),
            web.get("/oauth/users/me", self.get_user)
        ])
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| OAuth")
    
    async def oauth_callback(self, request: web.Request):
        req_json = await request.json()
        print(req_json)
        code = req_json.get("code")
        
        if code is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide a valid code"
            }, status=400)
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://discord.com/api/v10/oauth2/token", data={
                "client_id": "909559827330662470",
                "client_secret": "WUg-_jgTXE4IZ54cUC5_G2u66FZNbmk7",
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://unitedkp.me/login"
            }, headers={"Content-Type": "application/x-www-form-urlencoded"}) as resp:
                data = await resp.json()
        print(data)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": data
        }, status=200)
    
    async def get_user(self, request: web.Request):
        req_headers = request.headers
        token = req_headers.get("access_token")
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://discord.com/api/v10/users/@me", headers={
                "Authorization": f"Bearer {str(token)}"
            }) as req:
                data = await req.json()
        
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": data
        }, status=200)
