import aiohttp.web_app
from aiohttp import web


class RatesR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/rates", self.get_rate)
        ])
        print("🟡 | Rates")
    
    async def get_rate(self, request: web.Request):
        ...
        # TODO ZROBIĆ RATESY
