import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional
from pydantic import BaseModel

from ..database import get_session

router = APIRouter(tags=["Shops"])

LOG = logging.getLogger(__name__)

from api.model import Shop
from api.schema import GetProximityShops

class SetFavoriteShop(BaseModel):
    shop_id: int

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


# mettre en favori un magasin
@router.post("/favorite")
def set_favorite(body: SetFavoriteShop, session: Session = Depends(get_session)):
    print("SHOP ID :", body.shop_id)
    try:

        user_id = 1

        # Insertion dans la table de liaison (ajustez le nom de la table et des colonnes si besoin)
        sql_insert = text("""
            INSERT INTO magasin_favori (utilisateur_id, magasin_id) 
            VALUES (1, 1)
        """)
        session.execute(sql_insert, {"utilisateur_id": 1, "magasin_id": body.shop_id})
        session.commit()

        return {"message": "Magasin ajouté aux favoris avec succès."}

    except Exception as e:
        session.rollback()
        LOG.error(f"Erreur ajout favori magasin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# trouver les magasins les plus proche selon le GPS
@router.post("/proximity", response_model=list[Shop])
def get_product(body: GetProximityShops, session: Session = Depends(get_session)):
    try:
        # requête qui trouve les magasins dans un rayon donné et calcule la distance en km
        sql = text("""
            SELECT *, 
                   (sqrt(power(latitude - :latitude, 2) + power(longitude - :longitude, 2)) * 111.0) AS km 
            FROM magasin 
            WHERE sqrt(power(latitude - :latitude, 2) + power(longitude - :longitude, 2)) <= :radius_deg;
        """)
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
