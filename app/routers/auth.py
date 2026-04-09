from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db, db_dependency
from app.models import User
from app.schemas import CreateUserRequest, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)]
):
    payload = decode_token(token)

    user_id = payload.get("id")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate user")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Could not validate user")

    return user


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(request: CreateUserRequest, db: db_dependency):

    user = User(
        username=request.username,
        password=hash_password(request.password)
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

    return user


@router.post("/token")
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user: User | None = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401,
                            detail="Invalid credentials")

    token = create_access_token(user.username, user.id, user.role)

    return {"access_token": token, "token_type": "bearer"}
