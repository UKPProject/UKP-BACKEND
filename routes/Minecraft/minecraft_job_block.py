import aiohttp.web_app
from aiohttp import web
from colorama import Fore


class MinecraftJobBlock:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.get("/minecraft/job/block", self.create_new_job_block),
            web.post("/minecraft/job/block", self.create_new_job_block)
        ])
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| Business")
        
    async def create_new_job_block(self, request: web.Request):
        """
        req_json = await request.json()
        try:
            JobBlockM(req_json)
        except DataNotFilled:
            return web.json_response({
                "status_code": "400",
                "ctx": "json",
                "message": "data not filled"
            }, status=400)
        
        db = self.app['db']
        job_block_found = await db['job_block'].find_one({"name": str(req_json.get("name"))})
        if job_block_found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": f"job block with that name ({req_json.get('name')}) already exists"
            }, status=400)
        job_block_id_found = await db['job_block'].find_one({"job_blockId": str(req_json.get("job_blockId"))})
        if job_block_id_found is not None:
            return web.json_response({
                "status_code": "400",
                "ctx": "exists",
                "message": f"job block with that id ({req_json.get('job_blockId')}) already exists"
            }, status=400)
        new_job_block = await JobBlockM(req_json).data()
        await db['job_block'].insert_one(new_job_block)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": "job block created"
        }, status=200)
        """
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "data": {
                "player_salary": "100",
                "player_job": "egzorcysta za niecałe trzysta"
            }
        }, status=200)
    