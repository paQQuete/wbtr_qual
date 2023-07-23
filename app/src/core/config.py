import enum
import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic import BaseSettings, BaseModel
from .logger import LOGGING

logging_config.dictConfig(LOGGING)

DEBUG = True
if DEBUG:
    load_dotenv()


# class JWTAlgorithms(enum.Enum):
#     HS256 = "HS256"
#     HS384 = "HS384"
#     HS512 = "HS512"
#     RS256 = "RS256"
#     RS384 = "RS384"
#     RS512 = "RS512"
#     ES256 = "ES256"
#     ES384 = "ES384"
#     ES512 = "ES512"
#     PS256 = "PS256"
#     PS384 = "PS384"
#     PS512 = "PS512"


class Base(BaseSettings):
    class Config:
        env_file = '.env'


class DatabaseDSN(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str


class RedisDSN(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int


class Project(BaseSettings):
    PROJECT_NAME: str
    PROJECT_DOMAIN: str
    PROJECT_PORT: int
    DEBUG: bool


class JWT(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str


class Settings(BaseSettings):
    DB: DatabaseDSN = DatabaseDSN()
    PROJECT: Project = Project()
    REDIS: RedisDSN = RedisDSN()
    JWT: JWT = JWT()

    SQLALCHEMY_DATABASE_URL = \
        f"postgresql+asyncpg://{DB.POSTGRES_USER}:{DB.POSTGRES_PASSWORD}@{DB.POSTGRES_HOST}:{DB.POSTGRES_PORT}/{DB.POSTGRES_DB}"
    SQLALCHEMY_DATABASE_URL_SYNC = \
        f"postgresql://{DB.POSTGRES_USER}:{DB.POSTGRES_PASSWORD}@{DB.POSTGRES_HOST}:{DB.POSTGRES_PORT}/{DB.POSTGRES_DB}"

    PROJECT_URL = f"http://{PROJECT.PROJECT_DOMAIN}:{PROJECT.PROJECT_PORT}"

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ORM_ECHO: bool = True if PROJECT.DEBUG else False


SETTINGS = Settings()
