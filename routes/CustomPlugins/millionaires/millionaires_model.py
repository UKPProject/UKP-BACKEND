from enum import Enum
from typing import List, TypedDict

from tools.miscellaneous import DataNotFilled


class Answer:
    display: str
    value: int


class Lifeline(TypedDict):
    type: int
    used: bool


class MillionairesSession(TypedDict):
    user_snowflake: str
    mode: int
    step: int
    lifelines: List[Lifeline]
    leader_snowflake: str
    active: bool


class Question(TypedDict):
    question_content: str
    answers: List[Answer]
    prize: int
    q_id: int


class QuestionWithoutAnswers(TypedDict):
    question_content: str
    prize: int
    q_id: int


class QuestionM:
    def __init__(self, cursor: dict):
        try:
            self._question_content: str = cursor.get("question_content")
            self._answers: List[Answer] = cursor.get("answers")
            self._prize: int = cursor.get("prize")
            self._q_id: int = cursor.get("q_id")
        except TypeError:
            raise DataNotFilled

    async def data(self) -> Question:
        return {
            "question_content": str(self._question_content),
            "answers": self._answers,
            "prize": int(self._prize),
            "q_id": self._q_id
        }

    async def data_without_answers(self) -> QuestionWithoutAnswers:
        return {
            "question_content": str(self._question_content),
            "prize": int(self._prize),
            "q_id": self._q_id
        }
