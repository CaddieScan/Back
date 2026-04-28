from cffi.backend_ctypes import long
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

class CreateCart(BaseModel):
    utilisateur_id: int
    magasin_id: int

class AddProductToCart(BaseModel):
    panier_id: int
    produit_id: long
    quantite: int

class GetProximityShops(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50.0