import datetime
import uuid

from models.schemas.base import BaseSchemaModel, BaseFullModelMixin


class QuestionBase(BaseSchemaModel):
    id: int
    question: str
    answer: str
    question_created_at: datetime.datetime


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase, BaseFullModelMixin):
    uuid: uuid.UUID

    class Config:
        orm_mode = True
