from typing import TypedDict, List

from tools.miscellaneous import DataNotFilled


class News(TypedDict):
    _id: int
    title: str
    content: str
    attachments: List[str]
    content: str
    business: str
    author: str
    date: str


class NewsM:
    def __init__(self, cursor: dict):
        try:
            self._id: int = int(cursor.get("_id"))
            self._title: str = str(cursor.get("title"))
            self._attachments: List[str] = list(cursor.get("attachments"))
            self._content: str = str(cursor.get("content"))
            self._business: str = str(cursor.get("business"))
            self._author: str = str(cursor.get("author"))
            self._date: str = str(cursor.get("date"))
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> News:
        return {
            "_id": int(self._id),
            "title": str(self._title),
            "attachments": list(self._attachments),
            "content": str(self._content),
            "business": str(self._business),
            "author": str(self._author),
            "date": str(self._date)
        }


class CompanyNews(TypedDict):
    business: str
    news: List[News]
    owner: str


class CompanyNewsM:
    def __init__(self, cursor: dict):
        # init function for model for company all news
        try:
            self._business: str = str(cursor.get("business"))
            self._news: List[News] = cursor.get("news")
            self._owner: str = cursor.get("owner")
        except TypeError:
            raise DataNotFilled
    
    async def data(self) -> dict:
        return {
            "business": str(self._business),
            "news": list(self._news),
            "owner": str(self._owner)
        }
