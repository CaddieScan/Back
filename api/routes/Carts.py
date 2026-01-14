import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text

from ..database import get_session

router = APIRouter(tags=["Paniers"])

LOG = logging.getLogger(__name__)


from api.model import Carts

@router.post("/product/")
def create_product(body: Carts, session: Session = Depends(get_session)):
    try:
        sql = text("""
        INSERT INTO panier (utilisateur_id, magasin_id, code_barre, total_ttc, date_heure_creation)
        VALUES (:utilisateur_id, :magasin_id, :code_barre, :total_ttc, :date_heure_creation)
        RETURNING id;
        """)

        result = session.execute(
            sql,
            {
                "utilisateur_id": body.user_id,
                "magasin_id": body.shop_id,
                "code_barre": body.barcode,
                "total_ttc": body.total_price,
                "date_heure_creation": datetime.now(),
            }
        )

        inserted_id = result.scalar_one()

        session.commit()

        return {
            "id": inserted_id,
            "utilisateur_id": body.user_id,
            "magasin_id": body.shop_id,
            "code_barre": body.barcode,
            "total_ttc": body.total_price,
            "date_heure_creation": datetime.now(),
        }
    
        

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur insertion panier: {str(e)}"
        )
    

