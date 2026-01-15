from markdown_it.rules_block import table
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timedelta


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    username: str = Field(index=True, unique=True)

class Shop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    libelle: str = Field(index=True, unique=True)
    long: float
    lat: float
    logo: str

class Produit(SQLModel, table=True):
    code_barre: int = Field(default=None, primary_key=True)
    rayon_id: int
    promotion_id: Optional[int] = None
    libelle: str
    image: Optional[int] = None
    prix: float

class Carts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id : int
    shop_id : int
    barcode : int
    total_price : int
    creation_time : datetime = Field(default_factory=datetime.now)
