from typing import List, TypedDict

from tools.miscellaneous import DataNotFilled


class Rates(TypedDict):
    name: str
    code: str
    value: int
    icon: str
    oldValues: List[int]


class RatesM:
    def __init__(self, cursor: dict):
        try:
            self._name: str = str(cursor.get("name"))
            self._code: str = str(cursor.get("code"))
            self._value: int = int(cursor.get("value"))
            self._icon: str = str(cursor.get("icon"))
            self._oldValues: List[int] = list(cursor.get("oldValues"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> Rates:
        return {
            "name": str(self._name),
            "code": str(self._code),
            "value": int(self._value),
            "icon": str(self._icon),
            "oldValues": list(self._oldValues)
        }
