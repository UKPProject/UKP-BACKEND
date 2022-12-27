from typing import TypedDict

from tools.miscellaneous import DataNotFilled


class Bank(TypedDict):
    snowflake: str
    pseo: str
    balance: int
    job: str
    business: str
    socialCredits: int
    salary: int


class BankM:
    def __init__(self, cursor: dict):
        try:
            self._snowflake: str = str(cursor.get("snowflake"))
            self._pseo: str = str(cursor.get("pseo"))
            self._balance: int = int(cursor.get("balance"))
            self._job: str = str(cursor.get("job"))
            self._business: str = str(cursor.get("business"))
            self._socialCredits: int = int(cursor.get("socialCredits"))
            self._salary: int = int(cursor.get("salary"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Bank:
        return {
            "snowflake": str(self._snowflake),
            "pseo": str(self._pseo),
            "balance": int(self._balance),
            "job": str(self._job),
            "business": str(self._business),
            "socialCredits": int(self._socialCredits),
            "salary": int(self._salary)
        }
    {
        "snowflake": "698239897755975960",
        "pseo": "5-253492-AC1",
        "balance": 5063,
        "job": "Pracownik-imigrant w McDonalds",
        "business": "McDonalds",
        "socialCredits": 0,
        "salary": 1200
    }

