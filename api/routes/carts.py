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
        # Récupérer le prix du produit
        sql_prix = text("SELECT prix FROM produit WHERE code_barre = :produit_id")
        prix_result = session.execute(sql_prix, {"produit_id": body.produit_id}).scalar()

        if prix_result is None:
            raise HTTPException(status_code=404, detail="Produit non trouvé")

        prix_total = float(prix_result) * body.quantity

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

        # Mettre à jour le total_ttc du panier (ajouter le prix_total au total existant)
        sql_update = text("""
        UPDATE panier 
        SET total_ttc = COALESCE(total_ttc, 0) + :prix_total 
        WHERE id = :panier_id
        """)

        session.execute(
            sql_update,
            {
                "prix_total": prix_total,
                "panier_id": body.cart_id
            }
        )

        session.commit()

        return {
            "id": inserted_id,
            "panier_id": body.cart_id,
            "produit_id": body.produit_id,
            "quantite": body.quantity,
            "prix_ajoute": prix_total
        }

    except HTTPException as e:
        raise e
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



@router.get("/user/{user_id}/visites")
def get_user_carts_visites(user_id: int, session: Session = Depends(get_session)):
    try:
        sql = text("""
            SELECT 
                m.id AS magasin_id,
                m.libelle AS magasin_libelle, 
                m.chemin_absolut_logo AS magasin_logo,
                m.latitude AS magasin_latitude,
                m.longitude AS magasin_longitude,
                COUNT(p.id) AS nombre_visites
            FROM panier p
            JOIN magasin m ON p.magasin_id = m.id
            WHERE p.utilisateur_id = :user_id 
            GROUP BY m.id, m.libelle, m.chemin_absolut_logo, m.latitude, m.longitude
            ORDER BY nombre_visites DESC
        """)
        result = session.execute(sql, {"user_id": user_id})
        return [dict(row._mapping) for row in result]
    except Exception as e:
        LOG.error(f"Erreur récupération visites utilisateur: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
def get_user_carts(user_id: int, session: Session = Depends(get_session)):
    try:
        sql = text("""
            SELECT 
                p.*, 
                m.libelle AS magasin_libelle, 
                m.chemin_absolut_logo AS magasin_logo,
                m.latitude AS magasin_latitude,
                m.longitude AS magasin_longitude
            FROM panier p
            LEFT JOIN magasin m ON p.magasin_id = m.id
            WHERE p.utilisateur_id = :user_id 
            ORDER BY p.date_heure_creation DESC
        """)
        result = session.execute(sql, {"user_id": user_id})
        return [dict(row._mapping) for row in result]
    except Exception as e:
        LOG.error(f"Erreur récupération paniers utilisateur: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cart_id}/products")
def get_cart_products(cart_id: int, session: Session = Depends(get_session)):
    try:
        sql = text("""
            SELECT p.*, sp.quantite, sp.date_heure_creation as ajout_date
            FROM scan_panier sp
            JOIN produit p ON sp.produit_id = p.code_barre
            WHERE sp.panier_id = :cart_id
        """)
        result = session.execute(sql, {"cart_id": cart_id})
        return [dict(row._mapping) for row in result]
    except Exception as e:
        LOG.error(f"Erreur récupération produits du panier: {e}")
        raise HTTPException(status_code=500, detail=str(e))
