from typing import TypedDict

from tools.miscellaneous import DataNotFilled


class Bank(TypedDict):
    snowflake: str
    pseo: str
    balance: int
    job: str
    business: str
    businessId: str
    socialCredits: int
    dailySalary: int
    salary: int
    kingdom: str



class BankM:
    def __init__(self, cursor: dict):
        try:
            self._snowflake: str = str(cursor.get("snowflake"))
            self._pseo: str = str(cursor.get("pseo"))
            self._balance: int = int(cursor.get("balance"))
            self._job: str = str(cursor.get("job"))
            self._business: str = str(cursor.get("business"))
            self._businessId: str = str(cursor.get("businessId"))
            self._socialCredits: int = int(cursor.get("socialCredits"))
            self._dailySalary: int = int(cursor.get("dailySalary"))
            self._salary: int = int(cursor.get("salary"))
            self._kingdom: str = str(cursor.get("kingdom"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Bank:
        return {
            "snowflake": str(self._snowflake),
            "pseo": str(self._pseo),
            "balance": int(self._balance),
            "job": str(self._job),
            "business": str(self._business),
            "businessId": str(self._businessId),
            "socialCredits": int(self._socialCredits),
            "dailySalary": int(self._dailySalary),
            "salary": int(self._salary),
            "kingdom": str(self._kingdom)
        }

