from typing import List, TypedDict

from utils.exceptions import DataNotFilled


class Rates(TypedDict):
    name: str
    code: str
    value: float
    icon: str
    oldValues: List[float]


class RatesM:
    def __init__(self, cursor: dict):
        try:
            self._name: str = str(cursor.get("name"))
            self._code: str = str(cursor.get("code"))
            self._value: float = float(cursor.get("value"))
            self._icon: str = str(cursor.get("icon"))
            self._oldValues: List[float] = list(cursor.get("oldValues"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Rates:
        return {
            "name": str(self._name),
            "code": str(self._code),
            "value": float(self._value),
            "icon": str(self._icon),
            "oldValues": list(self._oldValues)
        }
