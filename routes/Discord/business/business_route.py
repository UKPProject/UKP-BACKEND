import aiohttp.web_app
from aiohttp import web
from colorama import Fore

from routes.Discord.business.business_model import BusinessM
from tools.miscellaneous import DataNotFilled


class BusinessR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/business", self.get_business),
            web.post("/business", self.create_business)
        ])
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| Business")
        
    async def create_business(self, request: web.Request):
        req_json = await request.json()
        try:
            BusinessM(req_json)
        except DataNotFilled:
            return web.json_response({
                "status_code": "400",
                "ctx": "json",
                "message": "data not filled"
            }, status=400)
        
        db = self.app['db']
        business_found = await db['business'].find_one({"name": str(req_json.get("name"))})
        if business_found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": f"business with that name ({req_json.get('name')}) already exists"
            }, status=400)
        business_id_found = await db['business'].find_one({"businessId": str(req_json.get("businessId"))})
        if business_id_found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": f"business with that id ({req_json.get('businessId')}) already exists"
            }, status=400)
        new_business = await BusinessM(req_json).data()
        await db['business'].insert_one(new_business)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": "business created"
        }, status=200)
    
    async def get_business(self, request: web.Request):
        req_headers = request.headers
        owner_snowflake = req_headers.get("owner_snowflake")
        name = req_headers.get("name")
        businessId = req_headers.get("businessId")
        if owner_snowflake and name is None and businessId is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "no one of possible queries found in request headers"
            }, status=400)
        db = self.app['db']
        if name is None and businessId is None:
            business_found = await db["business"].find_one({"ownerSnowflake": str(owner_snowflake)})
            business_data = await BusinessM(business_found).data()
            if business_found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": f"business with this owner snowflake ({owner_snowflake}) not found"
                }, status=400)
            return web.json_response({"status_code": "200", "ctx": "success", "message": business_data}, status=200)
            
        elif owner_snowflake is None and businessId is None:
            business_found = await db["business"].find_one({"businessId": str(name)})
            business_data = await BusinessM(business_found).data()
            if business_found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": f"business with this name ({name}) not found"
                }, status=400)
            return web.json_response({"status_code": "200", "ctx": "success", "message": business_data}, status=200)
        elif name is None and owner_snowflake is None:
            business_found = await db["business"].find_one({"businessId": str(businessId)})
            business_data = await BusinessM(business_found).data()
            if business_found is None:
                return web.json_response({
                    "status_code": "400",
                    "ctx": "not_found",
                    "message": f"business with this businessId ({businessId}) not found"
                }, status=400)
            return web.json_response({"status_code": "200", "ctx": "success", "message": business_data}, status=200)