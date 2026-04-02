from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_repeat: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateIn(BaseModel):
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)


class UserOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    email: EmailStr
    is_active: bool
    roles: list[str]


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserOut


class RuleOut(BaseModel):
    id: int
    role: str
    resource: str
    can_read: bool
    can_read_all: bool
    can_create: bool
    can_update: bool
    can_update_all: bool
    can_delete: bool
    can_delete_all: bool


class RuleUpdateIn(BaseModel):
    can_read: bool
    can_read_all: bool
    can_create: bool
    can_update: bool
    can_update_all: bool
    can_delete: bool
    can_delete_all: bool


class MockObjectOut(BaseModel):
    id: int
    owner_id: int
    title: str


Action = Literal["read", "create", "update", "delete"]
