import datetime
import re
import uuid
import enum

from sqlalchemy import Column, Integer, DateTime, Enum, String, ForeignKey, Float, Boolean, Index, UniqueConstraint
from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy.orm import relationship, validates

from db.database import Base


class DefaultMixin:
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4())
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class HTTPErrorDetails(enum.Enum):
    NOT_FOUND = 'Not found this entity'
    NOT_ACCEPTABLE = 'This operation is not available for this entity'
    UNPROCESSABLE_ENTITY = 'This entity cannot be processed'
    BAD_REQUEST = 'Invalid data provided'
    CONFLICT = 'Provided data already exists'
    UNAUTHORIZED = 'You are not authorized for this request'


class Users(DefaultMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'content'}

    username = Column(String(length=100), nullable=False, index=True, unique=True)
    email = Column(String(length=255), nullable=False, index=True, unique=True)
    password_hash = Column(String(length=512), nullable=False)
    first_name = Column(String(length=255), nullable=True)
    last_name = Column(String(length=255), nullable=True)

    refresh_tokens = relationship('RefreshTokens', back_populates='user')

    @validates('email')
    def validate_email(self, key, value):
        if not value:
            raise AssertionError('No email provided')
        if not re.match(r"^(.+)(\@)(\w+)(\.)(\w{2,30})$", value):
            raise AssertionError('Provided email is not an email address')
        return value

    @validates('password_hash')
    def validate_password_hash(self, key, value):
        if not value:
            raise AssertionError('No password hash provided')
        if not re.match(r'^\$2[ayb]\$.{56}$', value):
            raise AssertionError('Provided password hash is not a bcrypt hash')
        return value


class RefreshTokens(DefaultMixin, Base):
    __tablename__ = 'refresh_tokens'
    __table_args__ = (UniqueConstraint('useragent', 'user_id', name='ua_user_uniq_constr'),
                      {'schema': 'content'},
                      )

    refresh_token = Column(String, nullable=False, unique=True)
    useragent = Column(String, nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey('content.users.id', ondelete='CASCADE'), nullable=False)

