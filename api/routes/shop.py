import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Shops"])

LOG = logging.getLogger(__name__)

from api.model import Shop
from api.schema import GetProximityShops

# trouver tous les magasins de la BDD
@router.get("/all", response_model=list[Shop])
def get_product(session: Session = Depends(get_session)):
    try:
        sql = text("SELECT * FROM magasin")
        row = session.execute(sql)

        if row is None:
            raise HTTPException(status_code=404, detail="Magasin non trouvé")

        shops = []

        for r in row:
            LOG.info(f"Row: {r}")
            shop = Shop(**r._mapping)
            shops.append(shop)

        LOG.info(f"Magasins trouvés: {shops}")
        return shops

    except Exception as e:
        LOG.error(f"Erreur récupération magasins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# trouver les magasins les plus proche selon le GPS
@router.get("/proximity", response_model=list[Shop])
def get_product(body: GetProximityShops, session: Session = Depends(get_session)):
    try:
        # requête qui trouve les magasins dans un rayon donné
        sql = text("SELECT * FROM magasin WHERE sqrt(power(latitude - :latitude, 2) + power(longitude - :longitude, 2)) <= :radius_deg;")
        row = session.execute(
            sql,
            {
                "latitude": body.latitude,
                "longitude": body.longitude,
                # on convertit les km en degrés approximativement
                "radius_deg": body.radius_km / 111.0,
            }
        )

        if row is None:
            raise HTTPException(status_code=404, detail="Magasin non trouvé")

        shops = []

        for r in row:
            LOG.info(f"Row: {r}")
            shop = Shop(**r._mapping)
            shops.append(shop)

        LOG.info(f"Magasins trouvés: {shops}")
        return shops


    except Exception as e:
        LOG.error(f"Erreur récupération produit: {e}")
        raise HTTPException(status_code=500, detail=str(e))
