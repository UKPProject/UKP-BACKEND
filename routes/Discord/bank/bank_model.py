from typing import TypedDict

from utils.exceptions import DataNotFilled


class Bank(TypedDict):
    snowflake: str
    pseo: str
    balance: float
    job: str
    business: str
    socialCredits: float
    salary: float


class BankM:
    def __init__(self, cursor: dict):
        try:
            self._snowflake: str = str(cursor.get("snowflake"))
            self._pseo: str = str(cursor.get("pseo"))
            self._balance: float = float(cursor.get("balance"))
            self._job: str = str(cursor.get("job"))
            self._business: str = str(cursor.get("business"))
            self._socialCredits: float = float(cursor.get("socialCredits"))
            self._salary: float = float(cursor.get("salary"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Bank:
        return {
            "snowflake": str(self._snowflake),
            "pseo": str(self._pseo),
            "balance": float(self._balance),
            "job": str(self._job),
            "business": str(self._business),
            "socialCredits": float(self._socialCredits),
            "salary": float(self._salary)
        }

