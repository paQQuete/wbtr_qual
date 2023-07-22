from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models.models import HTTPErrorDetails
from models.schemas.auth import UserCreate, User
from db.database import get_db

router = APIRouter()

