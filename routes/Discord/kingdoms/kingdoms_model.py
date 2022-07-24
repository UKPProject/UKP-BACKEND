from typing import List, Dict, Union


class KingdomsM:
    def __init__(self, cursor: dict):
        self._name: str = str(cursor.get('name'))
        self._kings: List[str] = list(cursor.get('kings'))
        self._princes: List[str] = list(cursor.get('princes'))
        self._description: str = str(cursor.get('description'))
        self._money: str = str(cursor.get('money'))
        self._population: str = str(cursor.get('population'))
        self._cities: List[str] = list(cursor.get('cities'))
        self._capital: str = str(cursor.get('capital'))
        self._currency: str = str(cursor.get('currency'))
        self._territory: str = str(cursor.get('territory'))
        self._alliances: List[str] = list(cursor.get("alliances"))
    
    async def data(self) -> Dict[str, Union[str, List[str]]]:
        return {
            "name": str(self._name),
            "kings": list(self._kings),
            "cities": list(self._cities),
            "capital": str(self._capital),
            "princes": list(self._princes),
            "description": str(self._description),
            "money": str(self._money),
            "population": str(self._population),
            "currency": str(self._currency),
            "territory": str(self._territory),
            "alliances": list(self._alliances)
        }
    
    @property
    def name(self) -> str:
        return str(self._name)
    
    @property
    def kings(self) -> List[str]:
        return list(self._kings)
    
    @property
    def territory(self) -> str:
        return str(self._territory)
    
    @property
    def currency(self) -> str:
        return str(self._currency)
    
    @property
    def cities(self) -> List[str]:
        return list(self._cities)
    
    @property
    def capital(self) -> str:
        return str(self._capital)
    
    @property
    def princes(self) -> List[str]:
        return list(self._princes)
    
    @property
    def description(self) -> str:
        return str(self._description)
    
    @property
    def money(self) -> str:
        return str(self._money)
    
    @property
    def population(self) -> str:
        return str(self._population)
