import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlmodel import Session

from api.model import Shop
from api.schema import GetProximityShops

from ..database import get_session
from .web_common import (
    StoreCreate,
    StoreRead,
    StoreUpdate,
    ensure_carte_magasin_donnee_table,
    get_store_row_or_404,
    next_id,
    store_to_read,
)

router = APIRouter(tags=["Shops"])
api_router = APIRouter(prefix="/api", tags=["Shops"])

LOG = logging.getLogger(__name__)

PROXIMITY_CACHE = {}
CACHE_TTL = 300


class SetFavoriteShop(BaseModel):
    shop_id: int


@router.get("/all", response_model=list[Shop])
def get_shops(session: Session = Depends(get_session)):
    try:
        rows = session.execute(text("SELECT * FROM magasin"))
        shops = [Shop(**row._mapping) for row in rows]
        LOG.info("Magasins trouves: %s", shops)
        return shops
    except Exception as exc:
        LOG.error("Erreur recuperation magasins: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/favorite")
def set_favorite(body: SetFavoriteShop, session: Session = Depends(get_session)):
    try:
        session.execute(
            text(
                """
                INSERT INTO magasin_favori (utilisateur_id, magasin_id)
                VALUES (:utilisateur_id, :magasin_id)
                """
            ),
            {"utilisateur_id": 1, "magasin_id": body.shop_id},
        )
        session.commit()
        return {"message": "Magasin ajoute aux favoris avec succes."}
    except Exception as exc:
        session.rollback()
        LOG.error("Erreur ajout favori magasin: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


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
    _delete_store_rows(store_id, "store_id", session)
    return None


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shop(shop_id: int, session: Session = Depends(get_session)):
    _delete_store_rows(shop_id, "shop_id", session)
    return None


@router.post("/proximity", response_model=list[Shop])
def get_proximity_shops(
    body: GetProximityShops,
    user_id: int = 1,
    session: Session = Depends(get_session),
):
    cache_key = f"{body.latitude}_{body.longitude}_{body.radius_km}_{user_id}"
    current_time = time.time()

    if cache_key in PROXIMITY_CACHE:
        cached_result, timestamp = PROXIMITY_CACHE[cache_key]
        if current_time - timestamp < CACHE_TTL:
            LOG.info("Renvoi des magasins depuis le cache")
            return cached_result

    try:
        rows = session.execute(
            text(
                """
                SELECT *,
                       (sqrt(power(latitude - :latitude, 2) + power(longitude - :longitude, 2)) * 111.0) AS km,
                       EXISTS (
                           SELECT 1
                           FROM magasin_favori
                           WHERE utilisateur_id = :user_id
                             AND magasin_id = magasin.id
                       ) AS is_favorite
                FROM magasin
                WHERE sqrt(power(latitude - :latitude, 2) + power(longitude - :longitude, 2)) <= :radius_deg
                """
            ),
            {
                "latitude": body.latitude,
                "longitude": body.longitude,
                "radius_deg": body.radius_km / 111.0,
                "user_id": user_id,
            },
        )
        shops = [Shop(**row._mapping) for row in rows]
        PROXIMITY_CACHE[cache_key] = (shops, current_time)
        return shops
    except Exception as exc:
        LOG.error("Erreur recuperation magasins proches: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _delete_store_rows(store_id: int, param_name: str, session: Session):
    get_store_row_or_404(store_id, session)
    params = {param_name: store_id}
    placeholder = f":{param_name}"

    try:
        ensure_carte_magasin_donnee_table(session)
        session.execute(
            text(f"DELETE FROM carte_magasin_donnee WHERE magasin_id = {placeholder}"),
            params,
        )
        session.execute(
            text(f"DELETE FROM carte_magasin WHERE magasin_id = {placeholder}"),
            params,
        )
        session.execute(
            text(
                f"""
                DELETE FROM scan_panier
                WHERE produit_id IN (
                    SELECT p.code_barre
                    FROM produit p
                    JOIN rayon r ON r.id = p.rayon_id
                    WHERE r.magasin_id = {placeholder}
                )
                """
            ),
            params,
        )
        session.execute(
            text(
                f"""
                DELETE FROM produit
                WHERE rayon_id IN (SELECT id FROM rayon WHERE magasin_id = {placeholder})
                """
            ),
            params,
        )
        session.execute(text(f"DELETE FROM rayon WHERE magasin_id = {placeholder}"), params)
        session.execute(text(f"DELETE FROM etage WHERE magasin_id = {placeholder}"), params)
        session.execute(text(f"DELETE FROM magasin WHERE id = {placeholder}"), params)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Suppression impossible: {exc}",
        ) from exc
