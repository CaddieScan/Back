from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from model import User
from schema import CreateUser, UserRead
from database import get_session
from typing import List, Optional
from passlib.context import CryptContext

router = APIRouter()



@router.post("/", response_model=UserRead, tags=["users"])
def create_user(body: CreateUser, session: Session = Depends(get_session)) -> User:
    # Uniqueness checks
    existing_email = session.exec(select(User).where(User.email == body.email)).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email déjà utilisé",
        )

    existing_username = session.exec(select(User).where(User.username == body.username)).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nom d'utilisateur déjà utilisé",
        )

    hashed_password = body.password
    user = User(email=body.email, username=body.username, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=List[UserRead], tags=["users"])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=Optional[UserRead], tags=["users"])
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user
