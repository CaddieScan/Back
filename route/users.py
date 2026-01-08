from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from model import User
from schema import CreateUser
from database import get_session
from typing import List, Optional

router = APIRouter()


@router.post("/", response_model=User, tags=["users"])
def create_user(body: CreateUser, session: Session = Depends(get_session)) -> User:
    hashed_password = body.password + "notreallyhashed"  # Replace with real hashing
    user = User(email=body.email, hashed_password=hashed_password) # type: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=List[User], tags=["users"])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=Optional[User], tags=["users"])
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user
