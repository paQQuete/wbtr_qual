from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import HTTPErrorDetails
from models.schemas.auth import UserCreate, User
from db.database import get_db
from services.crud.users import create_user, get_user_by_email, get_user_by_username
from services.password import get_hashed_password, verify_password
from services.jwt import create_access_token, create_refresh_token

router = APIRouter()


@router.post('/signup', response_model=User)
async def signup_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db=db, email=data.email) or await get_user_by_username(db=db, username=data.username):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=HTTPErrorDetails.CONFLICT.value)

    data.password_hash = get_hashed_password(data.password_hash)
    return await create_user(db=db, user=data)


@router.post('/login')
async def login_user(email: Annotated[str, Form()], password: Annotated[str, Form()],
                     db: AsyncSession = Depends(get_db)):
    if not (user := await get_user_by_email(db=db, email=email)):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    if not verify_password(password=password, hashed_pass=user.password_hash):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=HTTPErrorDetails.BAD_REQUEST.value)
    return create_access_token(subject=user.id), create_refresh_token(subject=user.id)
