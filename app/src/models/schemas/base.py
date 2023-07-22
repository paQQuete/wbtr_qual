import datetime
from typing import Union

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseSchemaModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseFullModelMixin(BaseSchemaModel):
    created_at: datetime.datetime
    updated_at: Union[datetime.datetime, None]
