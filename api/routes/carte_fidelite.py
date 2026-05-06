from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, text

from ..model import CarteFidelite
from ..database import get_session
from ..schema import CreateCarteFidelite, CarteFideliteRead
from typing import List

import logging
LOG = logging.getLogger(__name__)

router = APIRouter()


# on crée une carte de fidélité
@router.post("/", response_model=CarteFidelite, tags=["carte_fidelite"])
def create_carte_fidelite(body: CreateCarteFidelite, session: Session = Depends(get_session)):
    try:
        sql = text("INSERT INTO carte_fidelite (utilisateur_id, magasin_id, code_barre) VALUES (:utilisateur_id, :magasin_id, :code_barre) RETURNING *")
        row = session.execute(sql, body.model_dump()).mappings().first()
        session.commit()
        return CarteFidelite(**row)
    except Exception as e:
        LOG.error(f"Erreur création carte de fidélité: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# on récupère toutes les cartes de fidélité d'un utilisateur avec le nom du magasin
@router.get("/user/{utilisateur_id}", response_model=List[CarteFideliteRead], tags=["carte_fidelite"])
def get_cartes_by_user(utilisateur_id: int, session: Session = Depends(get_session)):
    try:
        sql = text("SELECT cf.*, m.libelle as magasin_libelle FROM carte_fidelite cf JOIN magasin m ON m.id = cf.magasin_id WHERE cf.utilisateur_id = :utilisateur_id")
        rows = session.execute(sql, {"utilisateur_id": utilisateur_id}).mappings().all()

        if not rows:
            raise HTTPException(status_code=404, detail="Aucune carte trouvée pour cet utilisateur")

        return [CarteFideliteRead(**row) for row in rows]
    except Exception as e:
        LOG.error(f"Erreur récupération cartes: {e}")
        raise HTTPException(status_code=500, detail=str(e))