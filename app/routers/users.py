from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.database import db_dependency
from app.models import User, Loan
from app.routers.auth import get_current_user
from app.schemas import ChangePasswordRequest, UserResponse, LoanResponse
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])

user_dependency = Annotated[User, Depends(get_current_user)]


def require_admin(user: User):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.get("/me", response_model=UserResponse, status_code=200)
def get_me(user: user_dependency):
    return user


@router.put("/me/password", status_code=200)
def change_password(
        request: ChangePasswordRequest,
        db: db_dependency,
        user: user_dependency
):

    if not verify_password(request.current_password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    if request.current_password == request.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")

    user.password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password updated"}


@router.get("/me/loans", response_model=list[LoanResponse], status_code=200)
def get_my_loans(
    db: db_dependency,
    user: user_dependency,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    active: bool | None = None
):
    query = db.query(Loan).filter(Loan.user_id == user.id)

    if active:
        query = query.filter(Loan.return_date.is_(None))
    elif active is False:
        query = query.filter(Loan.return_date.is_not(None))

    return query.offset(skip).limit(limit).all()


@router.get("/", response_model=list[UserResponse], status_code=200)
def get_all_users(
        db: db_dependency,
        user: user_dependency,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    require_admin(user)
    return db.query(User).offset(skip).limit(limit).all()


@router.delete("/{user_id}", status_code=204)
def delete_user(
        db: db_dependency,
        user: user_dependency,
        user_id: int = Path(gt=0)
):
    require_admin(user)

    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    existing_loans = db.query(Loan).filter(
        Loan.user_id == user_id
    ).first()

    if existing_loans:
        raise HTTPException(
            status_code=400,
            detail="User cannot be deleted - has loan history"
        )

    db.delete(user_to_delete)
    db.commit()
