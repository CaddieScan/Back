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
    user_id: int
    shop_id: int

class AddProductToCart(BaseModel):
    cart_id: int
    produit_id: int
    quantity: int

class GetProximityShops(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50.0

class CreateCarteFidelite(BaseModel):
    utilisateur_id: int
    magasin_id: int
    code_barre: int

class CarteFideliteRead(BaseModel):
    id: int
    utilisateur_id: int
    magasin_id: int
    code_barre: int
    magasin_libelle: str