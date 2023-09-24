from typing import List, Tuple

import aiohttp.web_app
from aiohttp import web
from colorama import Fore

from routes.CustomPlugins.millionaires.millionaires_model import Answer, QuestionM, MillionairesSession, Lifeline
from tools.miscellaneous import log, DataNotFilled


class MillionairesR:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app: aiohttp.web_app.Application = app
        self.app.add_routes([
            web.post("/millionaires/question", self.add_new_question),
            web.get("/millionaires/questions", self.get_all_questions),
            web.get("/millionaires/question", self.get_question),
            web.post("/millionaires/session/start", self.start_new_session),
            web.get("/millionaires/session/get", self.get_session),
            web.put("/millionaires/session/lifeline", self.use_session_lifeline),
            web.put("/millionaires/session/step", self.update_session_step),
            web.delete("/millionaires/session/close", self.close_session),
            web.post("/millionaires/session/sync", self.sync_game)
        ])
        print(f"{Fore.CYAN}[INIT]{Fore.RESET}| Millionaires")

    async def sync_game(self, request: web.Request):
        req_json = await request.json()


    async def start_new_session(self, request: web.Request):
        req_json = await request.json()
        if req_json.get("user_snowflake") is not None and req_json.get("mode") is not None:
            check_sessions = [session async for session in
                              self.app['db']['MillionairesSessions'].find({"active": True})]
            if len(check_sessions) > 0:
                await log(request, 409)
                return web.json_response({
                    "status_code": "409",
                    "ctx": "data",
                    "message": "There is already active session"
                }, status=409)

            new_session = MillionairesSession(
                leader_snowflake=str(req_json.get("leader_snowflake")),
                mode=int(req_json.get("mode")),
                user_snowflake=str(req_json.get("user_snowflake")),
                step=0,
                active=True,
                lifelines=[
                    Lifeline(type=0, used=False),
                    Lifeline(type=1, used=False),
                    Lifeline(type=2, used=False),
                    Lifeline(type=3, used=False)
                ]
            )
            print(new_session)

            await self.app['db']['MillionairesSessions'].insert_one(new_session)
            await log(request, 200)
            return web.json_response({
                "status_code": "200",
                "ctx": "success",
                "message": "Session started"
            }, status=200)
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)

    async def get_session(self, request: web.Request):
        req_json = await request.json()
        if req_json.get("user_snowflake") is not None:
            check_sessions = [session async for session in
                              self.app['db']['MillionairesSessions'].find({"active": True})]
            if len(check_sessions) == 0:
                await log(request, 404)
                return web.json_response({
                    "status_code": "404",
                    "ctx": "data",
                    "message": "There is no active session"
                }, status=404)
            else:
                await log(request, 200)
                return web.json_response({
                    "status_code": "200",
                    "ctx": "success",
                    "message": check_sessions[0]
                }, status=200)
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)

    async def close_session(self, request: web.Request):
        req_json = await request.json()
        if req_json.get("user_snowflake") is not None:
            check_sessions = [session async for session in
                              self.app['db']['MillionairesSessions'].find({"active": True})]
            if len(check_sessions) == 0:
                await log(request, 404)
                return web.json_response({
                    "status_code": "404",
                    "ctx": "data",
                    "message": "There is no active session"
                }, status=404)
            else:
                await self.app['db']['MillionairesSessions'].update_one(
                    {"active": True, "user_id": req_json.get("user_snowflake")}, {"$set": {"active": False}})
                await log(request, 200)
                return web.json_response({
                    "status_code": "200",
                    "ctx": "success",
                    "message": "Session closed"
                }, status=200)
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)

    async def use_session_lifeline(self, request: web.Request):
        req_json = await request.json()
        if req_json.get("user_snowflake") is not None and req_json.get("lifeline") is not None:
            check_sessions = [session async for session in
                              self.app['db']['MillionairesSessions'].find({"active": True})]
            if len(check_sessions) == 0:
                await log(request, 404)
                return web.json_response({
                    "status_code": "404",
                    "ctx": "data",
                    "message": "There is no active session"
                }, status=404)
            else:
                if check_sessions[0]["lifelines"][req_json.get("lifeline")]["used"]:
                    await log(request, 409)
                    return web.json_response({
                        "status_code": "409",
                        "ctx": "data",
                        "message": "This lifeline is already used"
                    }, status=409)
                else:
                    print(check_sessions[0]["lifelines"][req_json.get("lifeline")]["used"])

                    check_sessions[0]["lifelines"][req_json.get("lifeline")]["used"] = True
                    print(check_sessions[0]["lifelines"][req_json.get("lifeline")]["used"])
                    s = await self.app['db']['MillionairesSessions'].update_one({"active": True}, {
                        "$set": {"lifelines": check_sessions[0]['lifelines']}})
                    print(s)
                    await log(request, 200)
                    return web.json_response({
                        "status_code": "200",
                        "ctx": "success",
                        "message": "Lifeline used"
                    }, status=200)
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)

    async def update_session_step(self, request: web.Request):
        req_json = await request.json()
        if req_json.get("user_snowflake") is not None and req_json.get("step") is not None:
            check_sessions = [session async for session in
                              self.app['db']['MillionairesSessions'].find({"active": True})]
            if len(check_sessions) == 0:
                await log(request, 404)
                return web.json_response({
                    "status_code": "404",
                    "ctx": "data",
                    "message": "There is no active session"
                }, status=404)
            else:
                await self.app['db']['MillionairesSessions'].update_one(
                    {"active": True, "user_id": str(req_json.get("user_snowflake"))},
                    {"$set": {"step": int(req_json.get("step"))}})
                await log(request, 200)
                return web.json_response({
                    "status_code": "200",
                    "ctx": "success",
                    "message": "Step updated"
                }, status=200)
        else:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)

    async def add_new_question(self, request: web.Request):
        req_json = await request.json()
        try:
            await QuestionM(req_json).data()
        except DataNotFilled:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid data"
            }, status=400)
        parsed = await QuestionM(req_json).data()
        await self.app['db']["milionerzy"].insert_one(parsed)
        await log(request, 200)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": await QuestionM(req_json).data(),
        })

    async def get_all_questions(self, request: web.Request):
        questions = self.app['db']["milionerzy"].find({})
        parsed = []
        async for question in questions:
            parsed.append(await QuestionM(question).data_without_answers())
        await log(request, 200)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": parsed,
        }, status=200)

    async def get_question(self, request: web.Request):
        req_json = await request.json()
        q_id = req_json.get("q_id")
        if q_id is None:
            await log(request, 400)
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid question"
            }, status=400)
        found = await self.app['db']["milionerzy"].find_one({"q_id": int(q_id)})
        if found is None:
            return web.json_response({
                "status_code": "400",
                "ctx": "data",
                "message": "Please provide valid question"
            }, status=400)
        await self.app['db']["milionerzy"].delete_one({"q_id": int(q_id)})
        parsed = await QuestionM(found).data()
        await log(request, 200)
        return web.json_response({
            "status_code": "200",
            "ctx": "success",
            "message": parsed,
        }, status=200)
