from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.database import get_session
from api.routes.product import api_router as product_api_router

# Quoi ?
# Tests unitaires des routes API produits exposees pour le frontend.
# Comment ?
# On monte un mini FastAPI avec uniquement le router produits et une fausse session SQL.
# Pourquoi ?
# Valider le contrat JSON produit sans dependre de PostgreSQL ni de Docker.


class FakeResult:
    def __init__(self, rows=None):
        self.rows = rows or []

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


class FakeSession:
    # Quoi ?
    # Fausse base en memoire avec un magasin et un produit.
    # Comment ?
    # execute() reconnait les requetes SQL utilisees par les routes produits.
    # Pourquoi ?
    # Tester les reponses API de facon deterministe et rapide.
    def __init__(self):
        self.stores = [{"id": 1, "libelle": "Carrefour Centre", "latitude": 48.8566, "longitude": 2.3522}]
        self.products = [
            {
                "code_barre": 123456789,
                "libelle": "Chocolat",
                "image": "/images/chocolat.png",
                "prix": 2.5,
                "quantite": 12.0,
                "unite": "pcs",
                "categorie": "Epicerie",
                "magasin_id": 1,
            }
        ]

    def execute(self, statement, params=None):
        params = params or {}
        sql = str(statement).lower()

        if "select id, libelle, latitude, longitude" in sql and "where id = :store_id" in sql:
            rows = [store for store in self.stores if store["id"] == params["store_id"]]
            return FakeResult(rows)

        if "from produit p" in sql and "join rayon r" in sql and "p.code_barre = :product_id" in sql:
            rows = [
                product
                for product in self.products
                if product["magasin_id"] == params["store_id"]
                and product["code_barre"] == params["product_id"]
            ]
            return FakeResult(rows)

        if "from produit p" in sql and "join rayon r" in sql and "r.magasin_id = :store_id" in sql:
            rows = [product for product in self.products if product["magasin_id"] == params["store_id"]]
            return FakeResult(rows)

        return FakeResult()

    def commit(self):
        pass


def create_client():
    # Quoi ?
    # Cree un client HTTP de test.
    # Comment ?
    # On remplace get_session par FakeSession via dependency_overrides.
    # Pourquoi ?
    # Appeler les routes comme un vrai client sans ouvrir de serveur.
    fake_session = FakeSession()
    app = FastAPI()
    app.include_router(product_api_router)
    app.dependency_overrides[get_session] = lambda: fake_session
    return TestClient(app)


def test_list_products_by_store():
    # Quoi ?
    # Verifie la liste des produits d'un magasin.
    # Comment ?
    # Appel GET /api/stores/1/products puis comparaison du JSON complet.
    # Pourquoi ?
    # S'assurer que le frontend recoit les champs Product attendus.
    client = create_client()
    response = client.get("/api/stores/1/products")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 123456789,
            "storeId": 1,
            "name": "Chocolat",
            "category": "Epicerie",
            "price": 2.5,
            "quantity": 12.0,
            "unit": "pcs",
            "barcode": "123456789",
            "imageAssetPath": "/images/chocolat.png",
            "imageUrl": "/images/chocolat.png",
        }
    ]


def test_get_product_by_id():
    # Quoi ?
    # Verifie la recuperation d'un produit par son id.
    # Comment ?
    # Appel GET avec le code-barres utilise comme product_id.
    # Pourquoi ?
    # Garantir que le scan ou la selection produit retrouve le bon article.
    client = create_client()
    response = client.get("/api/stores/1/products/123456789")

    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Chocolat"
    assert product["price"] == 2.5
    assert product["barcode"] == "123456789"
    assert product["imageAssetPath"] == "/images/chocolat.png"


def test_get_product_not_found():
    # Quoi ?
    # Verifie le cas produit introuvable.
    # Comment ?
    # Appel GET avec un id absent de la fausse base.
    # Pourquoi ?
    # Confirmer que l'API renvoie une erreur claire au frontend.
    client = create_client()
    response = client.get("/api/stores/1/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Produit introuvable"
