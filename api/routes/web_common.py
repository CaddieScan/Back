import json
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, Field as PydanticField
from sqlalchemy import text
from sqlmodel import Session


class StoreCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StoreRead(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    quantity: float = 0
    unit: str = ""
    barcode: Optional[str] = None
    imageAssetPath: Optional[str] = None
    imageUrl: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    barcode: Optional[str] = None
    imageAssetPath: Optional[str] = None
    imageUrl: Optional[str] = None


class ProductRead(BaseModel):
    id: int
    storeId: int
    name: str
    category: str
    price: float
    quantity: float
    unit: str
    barcode: Optional[str] = None
    imageAssetPath: str
    imageUrl: Optional[str] = None


class BulkProductsCreate(BaseModel):
    products: list[ProductCreate]


class Point(BaseModel):
    x: float
    y: float


class Floor(BaseModel):
    id: str
    name: str
    order: int


class Category(BaseModel):
    id: str
    name: str
    color: str


class Zone(BaseModel):
    id: str
    floorId: str
    name: str
    categoryId: str
    x: float
    y: float
    w: float
    h: float
    shape: str = PydanticField(pattern="^(rect|circle)$")


class Wall(BaseModel):
    floorId: str
    points: list[Point]


class AisleNode(BaseModel):
    id: str
    floorId: str
    x: float
    y: float


class AisleEdge(BaseModel):
    fromNodeId: str
    toNodeId: str


class Aisle(BaseModel):
    nodes: list[AisleNode] = []
    edges: list[AisleEdge] = []


class POI(BaseModel):
    id: str
    floorId: str
    type: str = PydanticField(pattern="^(entry|exit|checkout)$")
    x: float
    y: float
    label: str = ""
    checkoutKind: str = PydanticField(default="selfCheckout", pattern="^(selfCheckout|cashier)$")
    paymentMode: str = PydanticField(default="cardOnly", pattern="^(cardOnly|cardAndCash)$")
    isAccessible: bool = False


class StoreMapPayload(BaseModel):
    floors: list[Floor] = []
    categories: list[Category] = []
    zones: list[Zone] = []
    walls: list[Wall] = []
    aisles: list[Aisle] = []
    pois: list[POI] = []


def next_id(session: Session, table_name: str) -> int:
    result = session.execute(text(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}"))
    return int(result.scalar_one())


def next_barcode(session: Session) -> int:
    result = session.execute(text("SELECT COALESCE(MAX(code_barre), 999999999999) + 1 FROM produit"))
    return int(result.scalar_one())


def store_to_read(row: Any) -> StoreRead:
    return StoreRead(
        id=row["id"],
        name=row["libelle"],
        latitude=row["latitude"] or 0,
        longitude=row["longitude"] or 0,
    )


def product_to_read(row: Any) -> ProductRead:
    barcode = int(row["code_barre"])
    image_path = row["image"] or ""
    return ProductRead(
        id=barcode,
        storeId=row["magasin_id"],
        name=row["libelle"],
        category=row["categorie"] or "",
        price=row["prix"],
        quantity=row.get("quantite") or 0,
        unit=row.get("unite") or "",
        barcode=str(barcode),
        imageAssetPath=image_path,
        imageUrl=image_path,
    )


def ensure_product_frontend_columns(session: Session):
    session.execute(text("ALTER TABLE produit ADD COLUMN IF NOT EXISTS quantite FLOAT DEFAULT 0"))
    session.execute(text("ALTER TABLE produit ADD COLUMN IF NOT EXISTS unite VARCHAR DEFAULT ''"))
    session.commit()


def get_store_row_or_404(store_id: int, session: Session):
    row = session.execute(
        text(
            """
            SELECT id, libelle, latitude, longitude
            FROM magasin
            WHERE id = :store_id
            """
        ),
        {"store_id": store_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Magasin introuvable")
    return row


def get_product_row_or_404(store_id: int, product_id: int, session: Session):
    row = session.execute(
        text(
            """
            SELECT
                p.code_barre,
                p.libelle,
                p.image,
                p.prix,
                p.quantite,
                p.unite,
                r.libelle AS categorie,
                r.magasin_id
            FROM produit p
            JOIN rayon r ON r.id = p.rayon_id
            WHERE p.code_barre = :product_id
              AND r.magasin_id = :store_id
            """
        ),
        {"store_id": store_id, "product_id": product_id},
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit introuvable")
    return row


def get_or_create_floor_id(store_id: int, session: Session) -> int:
    row = session.execute(
        text("SELECT id FROM etage WHERE magasin_id = :store_id ORDER BY numero, id LIMIT 1"),
        {"store_id": store_id},
    ).mappings().first()
    if row is not None:
        return row["id"]

    floor_id = next_id(session, "etage")
    session.execute(
        text(
            """
            INSERT INTO etage (id, magasin_id, numero)
            VALUES (:id, :magasin_id, :numero)
            """
        ),
        {"id": floor_id, "magasin_id": store_id, "numero": 0},
    )
    return floor_id


def get_or_create_rayon_id(store_id: int, category: str, session: Session) -> int:
    row = session.execute(
        text(
            """
            SELECT id
            FROM rayon
            WHERE magasin_id = :store_id AND libelle = :category
            ORDER BY id
            LIMIT 1
            """
        ),
        {"store_id": store_id, "category": category},
    ).mappings().first()
    if row is not None:
        return row["id"]

    rayon_id = next_id(session, "rayon")
    floor_id = get_or_create_floor_id(store_id, session)
    session.execute(
        text(
            """
            INSERT INTO rayon (
                id, magasin_id, etage_id, libelle,
                point1_x, point1_y, point2_x, point2_y
            )
            VALUES (
                :id, :magasin_id, :etage_id, :libelle,
                0, 0, 0, 0
            )
            """
        ),
        {"id": rayon_id, "magasin_id": store_id, "etage_id": floor_id, "libelle": category},
    )
    return rayon_id


def ensure_carte_magasin_donnee_table(session: Session):
    session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS carte_magasin_donnee (
                magasin_id integer PRIMARY KEY REFERENCES magasin(id),
                donnees jsonb NOT NULL,
                date_heure_modification timestamp NOT NULL
            )
            """
        )
    )


def map_data_to_payload(data: Any) -> StoreMapPayload:
    if isinstance(data, str):
        data = json.loads(data)
    return StoreMapPayload.model_validate(data)


def payload_to_map_data(payload: StoreMapPayload) -> str:
    return json.dumps(payload.model_dump())


def now() -> datetime:
    return datetime.now()
