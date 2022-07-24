from __main__ import app
from urllib.parse import quote

from quart import request

import aiohttp


@app.route("/routes/website/oauth/callback", methods=['POST'])
async def callback():
    req_json = await request.json
    code = req_json["code"]
    print(code)
    if not code:
        return {
            "code": 400,
            "message": "Please provide a valid code"
        }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://discord.com/api/v10/oauth2/token",
            data={
                "client_id": 974365585829937263,
                "client_secret": "hah ;)",
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "http://localhost:3000/login"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as resp:
            data = await resp.json()
    print(data)
    token = data['access_token']

    return {'access_token': token}

@app.route("/routes/website/users/me")
async def get_own_user():
    req_json = request.headers
    token = req_json.get("access_token")
    async with aiohttp.ClientSession() as session:
        async with session.get(url="https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bearer {str(token)}"
        }) as req:
            test = await req.json()
            print(test)
            return test