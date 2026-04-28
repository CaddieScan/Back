from markdown_it.rules_block import table
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timedelta


class User(SQLModel, table=True):
    __tablename__ = "utilisateur" # nom utiliser en base de donnée
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    username: str = Field(index=True, unique=True)

class Shop(SQLModel, table=True):
    __tablename__ = "magasin"
    id: Optional[int] = Field(default=None, primary_key=True)
    libelle: str = Field(index=True, unique=True)
    long: float
    lat: float
    logo: str

class Produit(SQLModel, table=True):
    __tablename__ = "produit"
    code_barre: int = Field(default=None, primary_key=True)
    rayon_id: int
    promotion_id: Optional[int] = None
    libelle: str
    image: Optional[str] = None
    prix: float

class Carts(SQLModel, table=True):
    __tablename__ = "panier"
    id: Optional[int] = Field(default=None, primary_key=True)
    utilisateur_id: int
    magasin_id: int
    code_barre: int
    total_ttc: int
    date_heure_creation: datetime = Field(default_factory=datetime.now)

class ScanPanier(SQLModel, table=True):
    __tablename__ = "scan_panier"
    id: Optional[int] = Field(default=None, primary_key=True)
    panier_id: int
    produit_id: int
    quantite: int
    date_heure_creation: datetime = Field(default_factory=datetime.now)