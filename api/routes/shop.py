import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Session
from sqlalchemy import text
from typing import Optional

from ..database import get_session

router = APIRouter(tags=["Shops"])

LOG = logging.getLogger(__name__)

from api.model import Shop
from api.schema import GetProximityShops
from .web_common import (
    StoreCreate,
    StoreRead,
    StoreUpdate,
    ensure_carte_magasin_donnee_table,
    get_store_row_or_404,
    next_id,
    store_to_read,
)

api_router = APIRouter(prefix="/api", tags=["Shops"])

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


@api_router.get("/stores", response_model=list[StoreRead])
def list_api_stores(session: Session = Depends(get_session)):
    rows = session.execute(
        text(
            """
            SELECT id, libelle, latitude, longitude
            FROM magasin
            ORDER BY id
            """
        )
    ).mappings().all()
    return [store_to_read(row) for row in rows]


@api_router.get("/stores/{store_id}", response_model=StoreRead)
def get_api_store(store_id: int, session: Session = Depends(get_session)):
    return store_to_read(get_store_row_or_404(store_id, session))


@api_router.post("/stores", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
def create_api_store(body: StoreCreate, session: Session = Depends(get_session)):
    store_id = next_id(session, "magasin")
    session.execute(
        text(
            """
            INSERT INTO magasin (id, libelle, longitude, latitude, chemin_absolut_logo)
            VALUES (:id, :libelle, :longitude, :latitude, :chemin_absolut_logo)
            """
        ),
        {
            "id": store_id,
            "libelle": body.name,
            "longitude": body.longitude,
            "latitude": body.latitude,
            "chemin_absolut_logo": "",
        },
    )
    session.commit()
    return get_api_store(store_id, session)


@api_router.put("/stores/{store_id}", response_model=StoreRead)
def update_api_store(store_id: int, body: StoreUpdate, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return get_api_store(store_id, session)

    values = {"store_id": store_id}
    assignments = []
    if "name" in updates:
        assignments.append("libelle = :libelle")
        values["libelle"] = updates["name"]
    if "latitude" in updates:
        assignments.append("latitude = :latitude")
        values["latitude"] = updates["latitude"]
    if "longitude" in updates:
        assignments.append("longitude = :longitude")
        values["longitude"] = updates["longitude"]

    session.execute(
        text(f"UPDATE magasin SET {', '.join(assignments)} WHERE id = :store_id"),
        values,
    )
    session.commit()
    return get_api_store(store_id, session)


@api_router.delete("/stores/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_store(store_id: int, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    try:
        ensure_carte_magasin_donnee_table(session)
        session.execute(text("DELETE FROM carte_magasin_donnee WHERE magasin_id = :store_id"), {"store_id": store_id})
        session.execute(text("DELETE FROM carte_magasin WHERE magasin_id = :store_id"), {"store_id": store_id})
        session.execute(
            text(
                """
                DELETE FROM scan_panier
                WHERE produit_id IN (
                    SELECT p.code_barre
                    FROM produit p
                    JOIN rayon r ON r.id = p.rayon_id
                    WHERE r.magasin_id = :store_id
                )
                """
            ),
            {"store_id": store_id},
        )
        session.execute(
            text(
                """
                DELETE FROM produit
                WHERE rayon_id IN (SELECT id FROM rayon WHERE magasin_id = :store_id)
                """
            ),
            {"store_id": store_id},
        )
        session.execute(text("DELETE FROM rayon WHERE magasin_id = :store_id"), {"store_id": store_id})
        session.execute(text("DELETE FROM etage WHERE magasin_id = :store_id"), {"store_id": store_id})
        session.execute(text("DELETE FROM magasin WHERE id = :store_id"), {"store_id": store_id})
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Suppression impossible: {exc}",
        )
    return None


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shop(shop_id: int, session: Session = Depends(get_session)):
    get_store_row_or_404(shop_id, session)
    try:
        ensure_carte_magasin_donnee_table(session)
        session.execute(text("DELETE FROM carte_magasin_donnee WHERE magasin_id = :shop_id"), {"shop_id": shop_id})
        session.execute(text("DELETE FROM carte_magasin WHERE magasin_id = :shop_id"), {"shop_id": shop_id})
        session.execute(
            text(
                """
                DELETE FROM scan_panier
                WHERE produit_id IN (
                    SELECT p.code_barre
                    FROM produit p
                    JOIN rayon r ON r.id = p.rayon_id
                    WHERE r.magasin_id = :shop_id
                )
                """
            ),
            {"shop_id": shop_id},
        )
        session.execute(
            text(
                """
                DELETE FROM produit
                WHERE rayon_id IN (SELECT id FROM rayon WHERE magasin_id = :shop_id)
                """
            ),
            {"shop_id": shop_id},
        )
        session.execute(text("DELETE FROM rayon WHERE magasin_id = :shop_id"), {"shop_id": shop_id})
        session.execute(text("DELETE FROM etage WHERE magasin_id = :shop_id"), {"shop_id": shop_id})
        session.execute(text("DELETE FROM magasin WHERE id = :shop_id"), {"shop_id": shop_id})
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Suppression impossible: {exc}",
        )
    return None


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
