from typing import TypedDict, List


class Business(TypedDict):
    name: str
    employees: List[str]
    money: float
    address: str
    description: str
    ownerSnowflake: str
    jobs: List[str]

    # yes
    