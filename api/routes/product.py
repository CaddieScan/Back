import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Products"])

LOG = logging.getLogger(__name__)

from api.model import Produit
from .web_common import (
    BulkProductsCreate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ensure_product_frontend_columns,
    get_or_create_rayon_id,
    get_product_row_or_404,
    get_store_row_or_404,
    next_barcode,
    product_to_read,
)

api_router = APIRouter(prefix="/api", tags=["Products"])


@router.post("/product/")
def create_product(body: Produit, session: Session = Depends(get_session)):
    try:
        sql = text("""
        INSERT INTO produit (code_barre, rayon_id, promotion_id, libelle, image, prix)
        VALUES (:code_barre, :rayon_id, :promotion_id, :libelle, :image, :prix)
        RETURNING code_barre;
        """)

        result = session.execute(
            sql,
            {
                "code_barre": body.code_barre,
                "rayon_id": body.rayon_id,
                "promotion_id": body.promotion_id,
                "libelle": body.libelle,
                "image": body.image,
                "prix": body.prix,
            }
        )

        session.commit()


        return {
            "code_barre": body.code_barre,
            "rayon_id": body.rayon_id,
            "promotion_id": body.promotion_id,
            "libelle": body.libelle,
            "image": body.image,
            "prix": body.prix,
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur insertion produit: {str(e)}"
        )
    

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, SQLModel
from sqlalchemy import text
from ..database import get_session

import logging
LOG = logging.getLogger(__name__)


@router.get("/get_product", response_model=Produit)
def get_product(barcode: int, session: Session = Depends(get_session)):
    try:
        sql = text("SELECT * FROM produit WHERE code_barre = :barcode")
        row = session.execute(sql, {"barcode": barcode}).mappings().first()

        if row is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        product = Produit(**row)

        LOG.info(f"Produit trouvé: {product}")
        return product

    except HTTPException:
        raise
    except Exception as e:
        LOG.error(f"Erreur récupération produit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_product_by_barcode", response_model=Produit)
def get_product(barcode: int, session: Session = Depends(get_session)):
    try:
        sql = text("SELECT * FROM produit WHERE code_barre = :barcode")
        row = session.execute(sql, {"barcode": barcode}).mappings().first()

        if row is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        product = Produit(**row)

        LOG.info(f"Produit trouvé: {product}")
        return product

    except Exception as e:
        LOG.error(f"Erreur récupération produit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_products_by_shopid", response_model=list[Produit])
def get_products_by_shopid(shop_id: int, session: Session = Depends(get_session)):
    try:
        sql = text("SELECT p.* FROM produit p JOIN scan_panier sp ON p.code_barre = sp.produit_id JOIN panier pa ON sp.panier_id = pa.id WHERE pa.magasin_id = :shop_id")
        rows = session.execute(sql, {"shop_id": shop_id}).mappings().all()

        if not rows:
            raise HTTPException(status_code=404, detail="Produits non trouvés pour ce magasin")

        products = [Produit(**row) for row in rows]

        LOG.info(f"Produits trouvés: {products}")
        return products

    except Exception as e:
        LOG.error(f"Erreur récupération produits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stores/{store_id}/products", response_model=list[ProductRead])
def list_api_products(store_id: int, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_product_frontend_columns(session)
    rows = session.execute(
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
            WHERE r.magasin_id = :store_id
            ORDER BY p.libelle, p.code_barre
            """
        ),
        {"store_id": store_id},
    ).mappings().all()
    return [product_to_read(row) for row in rows]


@api_router.get("/stores/{store_id}/products/{product_id}", response_model=ProductRead)
def get_api_product(store_id: int, product_id: int, session: Session = Depends(get_session)):
    ensure_product_frontend_columns(session)
    return product_to_read(get_product_row_or_404(store_id, product_id, session))


@api_router.post("/stores/{store_id}/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_api_product(store_id: int, body: ProductCreate, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_product_frontend_columns(session)
    barcode = int(body.barcode) if body.barcode else next_barcode(session)
    rayon_id = get_or_create_rayon_id(store_id, body.category, session)
    session.execute(
        text(
            """
            INSERT INTO produit (code_barre, rayon_id, promotion_id, libelle, image, prix, quantite, unite)
            VALUES (:code_barre, :rayon_id, NULL, :libelle, :image, :prix, :quantite, :unite)
            """
        ),
        {
            "code_barre": barcode,
            "rayon_id": rayon_id,
            "libelle": body.name,
            "image": body.imageAssetPath or body.imageUrl,
            "prix": body.price,
            "quantite": body.quantity,
            "unite": body.unit,
        },
    )
    session.commit()
    return get_api_product(store_id, barcode, session)


@api_router.post(
    "/stores/{store_id}/products/bulk",
    response_model=list[ProductRead],
    status_code=status.HTTP_201_CREATED,
)
def create_api_products_bulk(store_id: int, body: BulkProductsCreate, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_product_frontend_columns(session)
    created_ids = []
    try:
        for item in body.products:
            barcode = int(item.barcode) if item.barcode else next_barcode(session)
            rayon_id = get_or_create_rayon_id(store_id, item.category, session)
            session.execute(
                text(
                    """
                    INSERT INTO produit (code_barre, rayon_id, promotion_id, libelle, image, prix, quantite, unite)
                    VALUES (:code_barre, :rayon_id, NULL, :libelle, :image, :prix, :quantite, :unite)
                    """
                ),
                {
                    "code_barre": barcode,
                    "rayon_id": rayon_id,
                    "libelle": item.name,
                    "image": item.imageAssetPath or item.imageUrl,
                    "prix": item.price,
                    "quantite": item.quantity,
                    "unite": item.unit,
                },
            )
            created_ids.append(barcode)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur import produits: {exc}")

    return [get_api_product(store_id, product_id, session) for product_id in created_ids]


@api_router.put("/stores/{store_id}/products/{product_id}", response_model=ProductRead)
def update_api_product(
    store_id: int,
    product_id: int,
    body: ProductUpdate,
    session: Session = Depends(get_session),
):
    ensure_product_frontend_columns(session)
    get_product_row_or_404(store_id, product_id, session)
    updates = body.model_dump(exclude_unset=True)

    if "category" in updates:
        rayon_id = get_or_create_rayon_id(store_id, updates["category"], session)
        session.execute(
            text("UPDATE produit SET rayon_id = :rayon_id WHERE code_barre = :product_id"),
            {"rayon_id": rayon_id, "product_id": product_id},
        )

    values = {"product_id": product_id}
    assignments = []
    if "name" in updates:
        assignments.append("libelle = :libelle")
        values["libelle"] = updates["name"]
    if "price" in updates:
        assignments.append("prix = :prix")
        values["prix"] = updates["price"]
    if "quantity" in updates:
        assignments.append("quantite = :quantite")
        values["quantite"] = updates["quantity"]
    if "unit" in updates:
        assignments.append("unite = :unite")
        values["unite"] = updates["unit"]
    if "imageAssetPath" in updates:
        assignments.append("image = :image")
        values["image"] = updates["imageAssetPath"]
    elif "imageUrl" in updates:
        assignments.append("image = :image")
        values["image"] = updates["imageUrl"]

    if assignments:
        session.execute(
            text(f"UPDATE produit SET {', '.join(assignments)} WHERE code_barre = :product_id"),
            values,
        )
    session.commit()
    return get_api_product(store_id, product_id, session)


@api_router.delete("/stores/{store_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_product(store_id: int, product_id: int, session: Session = Depends(get_session)):
    ensure_product_frontend_columns(session)
    get_product_row_or_404(store_id, product_id, session)
    session.execute(text("DELETE FROM scan_panier WHERE produit_id = :product_id"), {"product_id": product_id})
    session.execute(text("DELETE FROM produit WHERE code_barre = :product_id"), {"product_id": product_id})
    session.commit()
    return None
