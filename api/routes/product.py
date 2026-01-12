import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Products"])

LOG = logging.getLogger(__name__)


# 🔹 Schéma pour la requête (PAS une table)
class ProductCreate(SQLModel):
    code_barre: int
    rayon_id: int
    promotion_id: Optional[int] = None
    libelle: str
    image: Optional[int] = None
    prix: float


@router.post("/product/")
def create_product(body: ProductCreate, session: Session = Depends(get_session)):
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

        inserted_id = result.scalar_one()

        return {
            "code_barre": inserted_id,
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
    

@router.get("/get_product")
def get_product(barcode: int, session: Session = Depends(get_session)):
    try:
        sql = text("SELECT * FROM produit WHERE code_barre = :barcode")

        row = session.execute(sql, {"barcode": barcode}).first()

        if row is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        LOG.info(f"Produit trouvé: {dict(row._mapping)}")
        return dict(row._mapping)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
