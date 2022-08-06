import asyncio

import aiohttp.web_app

from routes.Discord.bank.bank_model import BankM
from routes.Discord.business.business_model import BusinessM


class UpdateSalary:
    def __init__(self, app: aiohttp.web_app.Application):
        self.app = app
        print("🟡 | UpdateSalary")
    
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
        
    async def update_salary(self):
        db = self.app['db']
        found_citizens = db["bank"].find({})
        pr = []
        async for citizen in found_citizens:
            pr.append(self.update_citizen(BankM(citizen)))
        await asyncio.gather(*pr)
        print("")