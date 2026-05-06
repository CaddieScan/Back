from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import text
import logging
from sqlmodel import Session

LOG = logging.getLogger(__name__)

from api.model import Rayon
from ..database import get_session
from .web_common import (
    StoreMapPayload,
    ensure_carte_magasin_donnee_table,
    get_store_row_or_404,
    map_data_to_payload,
    now,
    payload_to_map_data,
)


router = APIRouter(prefix="/api", tags=["Cartes magasin"])


@router.get("/stores/{store_id}/map", response_model=list[Rayon])
def get_store_map(store_id: int, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_carte_magasin_donnee_table(session)
    row = session.execute(
        text("SELECT * FROM rayon WHERE magasin_id = :store_id"),
        {"store_id": store_id},
    ).mappings().all()
    if row is None:
        raise HTTPException(status_code=404, detail="Rayon non trouvé")

    rayons = []

    for r in row:
        LOG.info(f"Row: {r}")
        rayon = Rayon(**r)
        rayons.append(rayon)
    LOG.info(f"Magasins trouvés: {rayons}")
    return rayons



@router.put("/stores/{store_id}/map", response_model=StoreMapPayload)
def save_store_map(store_id: int, body: StoreMapPayload, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_carte_magasin_donnee_table(session)
    session.execute(
        text(
            """
            INSERT INTO carte_magasin_donnee (magasin_id, donnees, date_heure_modification)
            VALUES (:magasin_id, CAST(:donnees AS jsonb), :date_heure_modification)
            ON CONFLICT (magasin_id) DO UPDATE SET
                donnees = EXCLUDED.donnees,
                date_heure_modification = EXCLUDED.date_heure_modification
            """
        ),
        {
            "magasin_id": store_id,
            "donnees": payload_to_map_data(body),
            "date_heure_modification": now(),
        },
    )
    session.commit()
    return body


@router.delete("/stores/{store_id}/map", status_code=status.HTTP_204_NO_CONTENT)
def delete_store_map(store_id: int, session: Session = Depends(get_session)):
    get_store_row_or_404(store_id, session)
    ensure_carte_magasin_donnee_table(session)
    session.execute(
        text("DELETE FROM carte_magasin_donnee WHERE magasin_id = :store_id"),
        {"store_id": store_id},
    )
    session.commit()
    return None
