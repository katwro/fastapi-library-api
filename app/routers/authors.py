from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import db_dependency
from app.models import Author, User
from app.routers.auth import get_current_user
from app.routers.users import require_admin
from app.schemas import AuthorResponse, CreateAuthorRequest, UpdateAuthorRequest

router = APIRouter(prefix="/authors", tags=["authors"])

user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=list[AuthorResponse], status_code=200)
def get_authors(
        db: db_dependency,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    return db.query(Author).offset(skip).limit(limit).all()


@router.get("/{author_id}", response_model=AuthorResponse, status_code=200)
def get_author(db: db_dependency, author_id: int = Path(gt=0)):
    author = db.query(Author).filter(Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author


@router.post("/", response_model=AuthorResponse, status_code=201)
def create_author(
        request: CreateAuthorRequest,
        db: db_dependency,
        user: user_dependency
):
    require_admin(user)

    author = Author(name=request.name)

    db.add(author)
    db.commit()
    db.refresh(author)

    return author


@router.put("/{author_id}", response_model=AuthorResponse, status_code=200)
def update_author(
        request: UpdateAuthorRequest,
        db: db_dependency,
        user: user_dependency,
        author_id: int = Path(gt=0)
):
    require_admin(user)

    author = db.query(Author).filter(Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = request.name
    db.commit()

    return author


@router.delete("/{author_id}", status_code=204)
def delete_author(
        db: db_dependency,
        user: user_dependency,
        author_id: int = Path(gt=0)
):
    require_admin(user)

    author = db.query(Author).filter(Author.id == author_id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    db.delete(author)
    db.commit()
