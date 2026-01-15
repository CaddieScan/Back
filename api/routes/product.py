import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Products"])

LOG = logging.getLogger(__name__)

from api.model import Produit


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
        sql = text("SELECT * FROM produit")
        row = session.execute(sql)

        if row is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        product = Produit(**row._mapping)

        LOG.info(f"Produit trouvé: {product}")
        return product

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
