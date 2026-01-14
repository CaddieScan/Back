import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Products"])

LOG = logging.getLogger(__name__)

from api.model import Product, Shop


@router.get("/get_product_by_barcode", response_model=Product)
def get_product(session: Session = Depends(get_session)):
    try:
        sql = text("SELECT * FROM magasin")
        row = session.execute(sql)


        if row is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        for r in row:
            LOG.info(f"Row: {r}")
            shop = Shop(**r._mapping)

        LOG.info(f"Produit trouvé: {shop}")
        return shop

    except Exception as e:
        LOG.error(f"Erreur récupération produit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
