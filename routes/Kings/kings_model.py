from typing import List, Dict, Union


class Kingdom:
    def __init__(self, cursor: dict):
        self._name: str = str(cursor['name'])
        self._kings: List[int] = list(cursor['kings'])
        self._description: str = str(cursor['description'])
        self._money: float = float(cursor['money'])
        self._population: int = int(cursor['population'])
    
    def data(self) -> Dict[str, Union[str, list, float, int]]:
        return {
            "name": str(self._name),
            "kings": list(self._kings),
            "description": str(self._description),
            "money": float(self._money),
            "population": int(self._population)
        }
        
    
    @property
    def name(self) -> str:
        return str(self._name)
    
    @property
    def kings(self) -> List[int]:
        return list(self._kings)
    
    @property
    def description(self) -> str:
        return str(self._description)
    
    @property
    def money(self) -> float:
        return float(self._money)
    
    @property
    def population(self) -> int:
        return int(self._population)
