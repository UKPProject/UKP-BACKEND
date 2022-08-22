import asyncio
import datetime
import random
import threading
from colorama import Fore
import aiohttp.web_app

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM


def wait_for_clock(hour, minute, result=None):
    t = datetime.datetime.combine(
        datetime.date.today(),
        datetime.time(hour, minute)
    )
    
    tt = datetime.datetime.now()
    
    if tt >= t:
        t += datetime.timedelta(days=1)
    
    delta = t - tt
    delta_sec = delta.seconds + delta.microseconds * 0.000001
    
    return asyncio.sleep(delta_sec, result)


class UpdateSalary:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app = app
        print(f"{Fore.YELLOW}[INIT]{Fore.RESET}| UpdateSalary")
        threading.Thread(target=asyncio.run, args=(self.update_rates(),)).start()
        threading.Thread(target=asyncio.run, args=(self.update_salary(),)).start()
    
    async def update_citizen(self, citizen: BankM):
        db = self.app['db']
        citizen_data = await citizen.data()
        
        found_business = await db['businesses'].find_one({"name": str(citizen_data.get("business"))})
        business = await BusinessM(found_business).data()
        
        employees = business.get("employees")
        for employee in employees:
            if str(employee.get("snowflake")) == str(citizen_data.get("snowflake")):
                await db['bank'].update_one(
                    {"snowflake": str(citizen_data.get("snowflake"))},
                    {"$set": {"salary": float(
                        round(
                            float(citizen_data.get("salary")) + float(employee.get("salary")),
                            2)
                    )
                    }}
                )
    
    async def update_rates(self):
        while True:
            db = self.app['db']
            found_rates = db["rates"].find({})
            async for rate in found_rates:
                await db["rates"].update_one(
                    {"code": str(rate.get("code"))},
                    {"$inc": {"value": int(random.randint((rate.get("value") - 2500), (rate.get("value") + 2500)))}}
                )
            print(f"{Fore.MAGENTA}[TASK]{Fore.RESET}| {datetime.datetime.now()} | Updated rates values")
            await asyncio.sleep(300)
            
    async def update_salary(self):
        while True:
            await wait_for_clock(0, 0)
            db = self.app['db']
            found_citizens = db["bank"].find({})
            pr = []
            async for citizen in found_citizens:
                pr.append(self.update_citizen(BankM(citizen)))
            await asyncio.gather(*pr)
            print(f"{Fore.MAGENTA}[TASKS]{Fore.RESET} | {datetime.datetime.now()} | Updated salaries limit")
            
        