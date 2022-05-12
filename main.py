import asyncio
import urllib.parse

from quart import Quart
from quart_cors import cors
from motor import motor_tornado

app = Quart(__name__)
app_cors = cors(app)

cluster = motor_tornado.MotorClient(
    'mongodb://admin:YcFTMUjsf9LB65vSQh@158.101.119.184:8654/ukp?authSource=admin')

app.db = cluster["ukp"]


if __name__ == '__main__':
    import routes.Kings.kings_route
    app.run(port=7556, host="0.0.0.0")
