from aiohttp import web
from routes.Discord.kingdoms.kingdoms_model import KingdomsM
from utils.exceptions import DataNotFilled


class KingdomsR:
    def __init__(self, app):
        self.app = app
        self.app.add_routes([
            web.get("/kingdoms", self.fetch_kingdoms),
            web.options("/kingdoms", self.get_kingdom),
            web.post("/kingdoms", self.create_kingdom)
        ])
        print("🟡 | Kingdoms")
        
    async def fetch_kingdoms(self, request: web.Request):
        db = self.app['db']["kingdoms"]
        found = db.find({})
        parsed = []
        async for doc in found:
            parsed.append(await KingdomsM(doc).data())
        
        return web.json_response(parsed, status=200)
    
    async def get_kingdom(self, request: web.Request):
        req_json = await request.json()
        kingdom_name = req_json.get("kingdom")
        if kingdom_name is None:
            return web.json_response({"status_code": "400", "message": "Please fill 'kingdom' field in request json"}, status=400)
        db = self.app['db']["kingdoms"]
        found = await db.find_one({"name": str(kingdom_name)})
        if found is None:
            return web.json_response({"status_code": "400", "message": f"Kingdom with name {kingdom_name} does not exist."}, status=400)
        final_kingdom = KingdomsM(found).data()
        return web.json_response(final_kingdom, status=200)
    
    async def create_kingdom(self, request:web.Request):
        req_json = await request.json()
        try:
            await KingdomsM(req_json).data()
        except DataNotFilled:
            return web.json_response({"status_code": "400", "message": "Please fill up all necessary data"}, status=400)
        db = self.app['db']["kingdoms"]
        data = await KingdomsM(req_json).data()
        found = await db.find_one({"name": str(data.get("name"))})
        if found is not None:
            return web.json_response({"status_code": "409", "message": "Kingdom with this name already exists"}, status=409)
        await db.insert_one(data)
        
        return web.json_response({"message": "Success!"}, status=200)
        