from typing import List, TypedDict


class Citizen(TypedDict):
    firstName: str
    lastName: str
    age: str
    kingdom: str
    snowflake: str
    pseo: str
    gender: str
    birthplace: str
    titles: List[str]
# yes
    birthday: str


class CitizenM:
    def __init__(self, cursor: dict):
        self._firstName: str = str(cursor.get("firstName"))
        self._lastName: str = str(cursor.get("lastName"))
        self._age: str = str(cursor.get("age"))
        self._kingdom: str = str(cursor.get("kingdom"))
        self._snowflake: str = str(cursor.get("snowflake"))
        self._pseo: str = str(cursor.get("pseo"))
        self._gender: str = str(cursor.get("gender"))
        self._birthplace: str = str(cursor.get("birthplace"))
        self._titles: List[str] = list(cursor.get("titles"))
        self._birthday: str = str(cursor.get("birthday"))
    
    async def data(self) -> Citizen:
        return {
            "firstName": str(self._firstName),
            "lastName": str(self._lastName),
            "age": str(self._age),
            "kingdom": str(self._kingdom),
            "pseo": str(self._pseo),
            "gender": str(self._gender),
            "birthplace": str(self._birthplace),
            "birthday": str(self._birthday),
            "titles": list(self._titles),
            "snowflake": str(self._snowflake)
        }
