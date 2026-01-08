from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    username: str
