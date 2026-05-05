from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timedelta


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(index=True, unique=True)
    hashed_password: Optional[str]
    username: Optional[str] = Field(index=True, unique=True)

class Shop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    libelle: Optional[str] = Field(index=True, unique=True)
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    logo: Optional[str] = None
    km: Optional[float] = None
    is_favorite: Optional[bool] = False

class Produit(SQLModel, table=True):
    code_barre: Optional[int] = Field(default=None, primary_key=True)
    rayon_id: int
    promotion_id: Optional[int] = None
    libelle: str
    image: Optional[str] = None
    prix: float

class Carts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id : int
    shop_id : int
    barcode : int
    total_price : int
    creation_time : datetime = Field(default_factory=datetime.now)
