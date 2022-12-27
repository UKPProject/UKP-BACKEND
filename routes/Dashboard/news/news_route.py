from aiohttp import web

from routes.Dashboard.news.news_model import CompanyNewsM
from routes.Discord.business.business_model import BusinessM
from tools.miscellaneous import log, DataNotFilled


class NewsR:
    def __init__(self, app: web.Application):
        self.app: web.Application = app
        self.app.add_routes([
            web.post("/news/company", self.create_news_company),
            web.post("/news/post", self.push_news)
        ])
    
    async def create_news_company(self, request: web.Request):
        req_json = await request.json()
        business_name = req_json.get("business_name")
        db = self.app['db']
        business_found = await db['business'].find_one({"name": str(business_name)})
        business = await BusinessM(business_found).data()
        if business_found is None:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "business",
                "message": f"company with that name ({business_name}) not found"
            }, status=400)
        
        new_news_company = await CompanyNewsM({
            "business": business.get("name"),
            "news": [],
            "owner": business.get("ownerSnowflake")
        }).data()
        
        await db['news'].insert_one(new_news_company)
        await log(request, 200)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": "news company created"
        }, status=200)
    
    async def post_news(self, request: web.Request):
        req_
    
