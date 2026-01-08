from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str
