from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str
