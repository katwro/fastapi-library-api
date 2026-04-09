from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CreateAuthorRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class UpdateAuthorRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class CreateBookRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=17, pattern = "^[0-9-]+$")
    author_ids: List[int] = Field(min_length=1)


class UpdateBookRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=17, pattern = "^[0-9-]+$")
    author_ids: Optional[List[int]] = Field(default=None, min_length=1)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=50)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)


class AuthorResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    id: int
    title: str
    isbn: Optional[str]
    available: bool
    authors: List[AuthorResponse]

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class BookSimple(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class LoanResponse(BaseModel):
    id: int
    loan_date: datetime
    return_date: Optional[datetime]

    user: UserSimple
    book: BookSimple

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True
