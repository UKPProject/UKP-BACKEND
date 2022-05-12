import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from main import app
from quart import request

from routes.Kings.kings_model import Kingdom
from utils.authorize import authorize


@app.route("/routes/kingdoms/fetch", methods=['GET', 'POST'])
@authorize(1)
async def fetch_kingdoms():
    start = time.monotonic()
    if request.method == 'GET':
        fetch = app.db.Kingdoms.find({})
        parsed = await fetch.to_list(length=40)
        element: dict
        kingdoms_list = []
        for element in parsed:
            kingdom = Kingdom(element)
            kingdoms_list.append(kingdom.data())
        return {
                   "data": kingdoms_list,
                   "code": 200,
                   "message": 'Ok!',
                   "time": round((time.monotonic() - start), 2)
               }, 200
    elif request.method == 'POST':
        req_json = await request.json
        if req_json is not None:
            kingdom_name = req_json["kingdom_name"]
            if kingdom_name is None:
                return {
                           "code": 400,
                           "message": 'Please fill "kingdom_name" in your json payload',
                           "time": round((time.monotonic() - start), 2)
                       }, 400
            else:
                found = await app.db.Kingdoms.find_one({"name": str(kingdom_name)})
                if found is None:
                    return {
                               "code": 400,
                               "message": f'Kingdom "{kingdom_name}" not found',
                               "time": round((time.monotonic() - start), 2)
                           }, 400
                kingdom = Kingdom(found)
                return {
                    "data": kingdom.data(),
                    "code": 200,
                    "message": 'Ok!',
                    "time": round((time.monotonic() - start), 2)
                }
        else:
            return {
                       "code": 400,
                       "message": 'Please fill "kingdom_name" in your json payload',
                       "time": round((time.monotonic() - start), 2)
                   }, 400
