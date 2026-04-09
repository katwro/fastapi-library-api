from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError

from app.database import db_dependency
from app.models import Book, Author, Loan, User
from app.routers.auth import get_current_user
from app.routers.users import require_admin
from app.schemas import CreateBookRequest, BookResponse, UpdateBookRequest

router = APIRouter(prefix="/books", tags=["books"])

user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=list[BookResponse], status_code=200)
def get_books(
        db: db_dependency,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        available: bool | None = None
):
    query = db.query(Book)

    if available is not None:
        query = query.filter(Book.available == available)

    return query.offset(skip).limit(limit).all()


@router.get("/{book_id}", response_model=BookResponse, status_code=200)
def get_book(db: db_dependency, book_id: int = Path(gt=0)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/", response_model=BookResponse, status_code=201)
def create_book(
        book_request: CreateBookRequest,
        db: db_dependency,
        user: user_dependency
):
    require_admin(user)

    authors = db.query(Author).filter(
        Author.id.in_(book_request.author_ids)
    ).all()

    if len(authors) != len(book_request.author_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more authors not found"
        )

    book = Book(
        title=book_request.title,
        isbn=book_request.isbn
    )

    book.authors = authors

    try:
        db.add(book)
        db.commit()
        db.refresh(book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Book with this ISBN already exists"
        )

    return book


@router.put("/{book_id}", response_model=BookResponse, status_code=200)
def update_book(
        db: db_dependency,
        book_request: UpdateBookRequest,
        user: user_dependency,
        book_id: int = Path(gt=0)
):
    require_admin(user)

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_request.title is not None:
        book.title = book_request.title

    if book_request.isbn is not None:
        book.isbn = book_request.isbn

    if book_request.author_ids is not None:

        authors = db.query(Author).filter(
            Author.id.in_(book_request.author_ids)
        ).all()

        if len(authors) != len(book_request.author_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more authors not found"
            )

        book.authors = authors

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Book with this ISBN already exists"
        )

    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(
        db: db_dependency,
        user: user_dependency,
        book_id: int = Path(gt=0)
):
    require_admin(user)

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    existing_loans = db.query(Loan).filter(
        Loan.book_id == book_id
    ).first()

    if existing_loans:
        raise HTTPException(
            status_code=400,
            detail="Book cannot be deleted - has loan history"
        )

    db.delete(book)
    db.commit()
