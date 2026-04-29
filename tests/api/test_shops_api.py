from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.database import get_session
from api.routes.shop import api_router as shop_api_router

# Quoi ?
# Tests unitaires des routes API magasins exposees pour le frontend.
# Comment ?
# On monte un mini FastAPI avec uniquement le router shops et une fausse session SQL.
# Pourquoi ?
# Valider le contrat JSON Store sans lancer PostgreSQL ni le backend complet.


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
    # Fausse base en memoire avec un magasin.
    # Comment ?
    # execute() renvoie les lignes attendues selon la requete SQL recue.
    # Pourquoi ?
    # Isoler les routes shops de la vraie base pendant les tests.
    def __init__(self):
        self.stores = [
            {
                "id": 1,
                "libelle": "Carrefour Centre",
                "latitude": 48.8566,
                "longitude": 2.3522,
            }
        ]

    def execute(self, statement, params=None):
        params = params or {}
        sql = str(statement).lower()

        if "select id, libelle, latitude, longitude" in sql and "where id = :store_id" in sql:
            rows = [store for store in self.stores if store["id"] == params["store_id"]]
            return FakeResult(rows)

        if "select id, libelle, latitude, longitude" in sql and "from magasin" in sql:
            return FakeResult(self.stores)

        return FakeResult()


def create_client():
    # Quoi ?
    # Cree un client HTTP de test.
    # Comment ?
    # On remplace get_session par FakeSession via dependency_overrides.
    # Pourquoi ?
    # Tester les endpoints comme des appels HTTP sans serveur externe.
    fake_session = FakeSession()
    app = FastAPI()
    app.include_router(shop_api_router)
    app.dependency_overrides[get_session] = lambda: fake_session
    return TestClient(app)


def test_list_stores():
    # Quoi ?
    # Verifie la liste des magasins.
    # Comment ?
    # Appel GET /api/stores puis comparaison du JSON complet.
    # Pourquoi ?
    # S'assurer que Flutter recoit id, name, latitude et longitude.
    client = create_client()
    response = client.get("/api/stores")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Carrefour Centre",
            "latitude": 48.8566,
            "longitude": 2.3522,
        }
    ]


def test_get_store():
    # Quoi ?
    # Verifie la recuperation d'un magasin par id.
    # Comment ?
    # Appel GET /api/stores/1 sur la fausse base.
    # Pourquoi ?
    # Garantir que la fiche magasin peut etre chargee individuellement.
    client = create_client()
    response = client.get("/api/stores/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Carrefour Centre"


def test_get_store_not_found():
    # Quoi ?
    # Verifie le cas magasin introuvable.
    # Comment ?
    # Appel GET avec un id absent de la fausse base.
    # Pourquoi ?
    # Confirmer que l'API renvoie une 404 exploitable par le frontend.
    client = create_client()
    response = client.get("/api/stores/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Magasin introuvable"
