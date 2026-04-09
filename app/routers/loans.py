from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import db_dependency
from app.models import Loan, Book, User
from app.routers.auth import get_current_user
from app.routers.users import require_admin
from app.schemas import LoanResponse

router = APIRouter(prefix="/loans", tags=["loans"])

user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=list[LoanResponse], status_code=200)
def get_all_loans(
        db: db_dependency,
        user: user_dependency,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    require_admin(user)
    return db.query(Loan).offset(skip).limit(limit).all()


@router.post("/{book_id}", status_code=201)
def borrow_book(
        db: db_dependency,
        user: user_dependency,
        book_id: int = Path(gt=0)
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    active_loan = db.query(Loan).filter(
        Loan.book_id == book_id,
        Loan.user_id == user.id,
        Loan.return_date.is_(None)
    ).first()

    if active_loan:
        raise HTTPException(
            status_code=400,
            detail="You have already borrowed this book"
        )

    if not book.available:
        raise HTTPException(status_code=400, detail="Book not available")

    loan = Loan(
        user_id=user.id,
        book_id=book_id,
        loan_date=datetime.now(timezone.utc),
        due_date=datetime.now(timezone.utc) + timedelta(days=14)
    )

    book.available = False

    db.add(loan)
    db.commit()
    db.refresh(loan)

    return {
        "loan_id": loan.id,
        "message": "Book borrowed successfully",
        "book_id": book.id,
        "title": book.title
    }


@router.put("/{loan_id}/return", status_code=200)
def return_book(
        db: db_dependency,
        user: user_dependency,
        loan_id: int = Path(gt=0)
):
    require_admin(user)

    loan = db.query(Loan).filter(Loan.id == loan_id).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")

    book = db.query(Book).filter(Book.id == loan.book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    loan.return_date = datetime.now(timezone.utc)
    book.available = True

    db.commit()

    return {
        "loan_id": loan.id,
        "message": "Book returned successfully",
        "book_id": book.id,
        "title": book.title
    }
