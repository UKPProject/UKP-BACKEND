from enum import Enum
from typing import TypedDict, List

from tools.miscellaneous import DataNotFilled


class Employee(TypedDict):
    snowflake: str
    pseo: str
    salary: int
    worked: int

class Business(TypedDict):
    name: str
    employees: List[Employee]
    money: int
    address: str
    description: str
    ownerSnowflake: str
    companyType: str
    jobs: List[str]
    businessId: str


class BusinessM:
    def __init__(self, cursor: dict):
        try:
            self._name: str = str(cursor.get("name"))
            self._employees: List[Employee] = list(cursor.get("employees"))
            self._money: int = int(cursor.get("money"))
            self._address: str = str(cursor.get("address"))
            self._description: str = str(cursor.get("description"))
            self._ownerSnowflake: str = str(cursor.get("ownerSnowflake"))
            self._companyType: str = cursor.get("companyType")
            self._jobs: List[str] = list(cursor.get("jobs"))
            self._businessId: str = str(cursor.get("businessId"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Business:
        return {
            "name": str(self._name),
            "employees": list(self._employees),
            "money": int(self._money),
            "address": str(self._address),
            "description": str(self._description),
            "ownerSnowflake": str(self._ownerSnowflake),
            "companyType": self._companyType,
            "jobs": list(self._jobs),
            "businessId": str(self._businessId)
        }

