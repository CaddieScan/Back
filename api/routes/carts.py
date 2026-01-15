import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text

from ..database import get_session

router = APIRouter(tags=["Paniers"])

LOG = logging.getLogger(__name__)

from api.schema import CreateCart, AddProductToCart

@router.post("/product/")
def add_product_to_cart(body: AddProductToCart, session: Session = Depends(get_session)):
    try:
        # insertion du produit dans le panier
        sql = text("""
        INSERT INTO scan_panier (panier_id, produit_id, quantite, date_heure_creation)
        VALUES (:panier_id, :produit_id, :quantite, :date_heure_creation)
        RETURNING id;
        """)

        result = session.execute(
            sql,
            {
                "panier_id": body.cart_id,
                "produit_id": body.produit_id,
                "quantite": body.quantity,
                "date_heure_creation": datetime.now(),
            }
        )

        inserted_id = result.scalar_one()

        session.commit()

        return {
            "id": inserted_id,
            "panier_id": body.cart_id,
            "produit_id": body.produit_id,
            "quantite": body.quantity,
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur insertion panier: {str(e)}"
        )
    

@router.post("/")
def create_cart(body: CreateCart, session: Session = Depends(get_session)):
    try:
        placeholder_code_barre = "0000000000000"
        sql = text("""
        INSERT INTO panier (utilisateur_id, magasin_id, date_heure_creation, code_barre, total_ttc)
        VALUES (:utilisateur_id, :magasin_id, :date_heure_creation, :code_barre, :total_ttc)
        RETURNING id;
        """)

        result = session.execute(
            sql,
            {
                "utilisateur_id": body.user_id,
                "magasin_id": body.shop_id,
                "date_heure_creation": datetime.now(),
                "code_barre": placeholder_code_barre,
                "total_ttc": 0,
            }
        )

        inserted_id = result.scalar_one()

        session.commit()

        return {
            "id": inserted_id,
            "utilisateur_id": body.user_id,
            "magasin_id": body.shop_id,
            "date_heure_creation": datetime.now(),
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création panier: {str(e)}"
        )