 # app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta

from app.dependencies import get_db
from app.models import User
from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_password_hash,
)

router = APIRouter(
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/signup")
def sign_up(signup: SignUpRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == signup.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists."
        )
    user = User(
        name=signup.name,
        email=signup.email,
        role="analyst",  # or your default role for new users
        password_hash=get_password_hash(signup.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "user_id": user.id}


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


class TokenJSON(BaseModel):
    username: str
    password: str


@router.post("/token_json", summary="Login (JSON)")
def login_json(
    creds: TokenJSON,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, creds.username, creds.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    access_token = create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
