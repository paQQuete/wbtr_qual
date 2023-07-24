import datetime
import uuid

from models.schemas.base import BaseSchemaModel, BaseFullModelMixin


class JWTSchema(BaseSchemaModel):
    exp: datetime.datetime
    sub: uuid.UUID
    iss: str
    nbf: datetime.datetime
    jti: uuid.UUID
    iat: datetime.datetime
