import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.database import get_session
from api.routes.store_map import router as store_map_router

# Quoi ?
# Tests unitaires des routes API de carte magasin.
# Comment ?
# On monte un mini FastAPI avec uniquement le router map et une fausse session SQL.
# Pourquoi ?
# Verifier sauvegarde, rechargement et suppression sans toucher a PostgreSQL.


class FakeResult:
    def __init__(self, rows=None):
        self.rows = rows or []

    def mappings(self):
        return self

    def first(self):
        return self.rows[0] if self.rows else None


class FakeSession:
    # Quoi ?
    # Fausse base en memoire avec un magasin et un stockage de map.
    # Comment ?
    # execute() simule les SELECT, INSERT et DELETE sur carte_magasin_donnee.
    # Pourquoi ?
    # Tester le cycle complet de la map avec des donnees controlees.
    def __init__(self):
        self.stores = [{"id": 1, "libelle": "Carrefour Centre", "latitude": 48.8566, "longitude": 2.3522}]
        self.maps = {}

    def execute(self, statement, params=None):
        params = params or {}
        sql = str(statement).lower()

        if "create table if not exists carte_magasin_donnee" in sql:
            return FakeResult()

        if "select id, libelle, latitude, longitude" in sql and "where id = :store_id" in sql:
            rows = [store for store in self.stores if store["id"] == params["store_id"]]
            return FakeResult(rows)

        if "select donnees from carte_magasin_donnee" in sql:
            store_id = params["store_id"]
            if store_id not in self.maps:
                return FakeResult()
            return FakeResult([{"donnees": self.maps[store_id]}])

        if "insert into carte_magasin_donnee" in sql:
            self.maps[params["magasin_id"]] = json.loads(params["donnees"])
            return FakeResult()

        if "delete from carte_magasin_donnee" in sql:
            self.maps.pop(params["store_id"], None)
            return FakeResult()

        return FakeResult()

    def commit(self):
        pass


def create_client():
    # Quoi ?
    # Cree un client HTTP de test.
    # Comment ?
    # On remplace get_session par FakeSession via dependency_overrides.
    # Pourquoi ?
    # Appeler les routes map comme le frontend, sans serveur reel.
    fake_session = FakeSession()
    app = FastAPI()
    app.include_router(store_map_router)
    app.dependency_overrides[get_session] = lambda: fake_session
    return TestClient(app)


def test_get_empty_store_map():
    # Quoi ?
    # Verifie le chargement d'une map absente.
    # Comment ?
    # Appel GET /api/stores/1/map sans donnees enregistrees.
    # Pourquoi ?
    # Le frontend doit recevoir une map vide exploitable au premier chargement.
    client = create_client()
    response = client.get("/api/stores/1/map")

    assert response.status_code == 200
    assert response.json() == {
        "floors": [],
        "categories": [],
        "zones": [],
        "walls": [],
        "aisles": [],
        "pois": [],
    }


def test_save_and_reload_store_map():
    # Quoi ?
    # Verifie la sauvegarde puis le rechargement d'une map complete.
    # Comment ?
    # Appel PUT avec floors, categories, zones, walls, aisles et pois, puis GET.
    # Pourquoi ?
    # Garantir que l'editeur Flutter peut retrouver exactement la map sauvegardee.
    client = create_client()
    payload = {
        "floors": [{"id": "floor-1", "name": "RDC", "order": 0}],
        "categories": [{"id": "cat-1", "name": "Epicerie", "color": "#ffcc00"}],
        "zones": [
            {
                "id": "zone-1",
                "floorId": "floor-1",
                "name": "Rayon chocolat",
                "categoryId": "cat-1",
                "x": 10,
                "y": 20,
                "w": 100,
                "h": 50,
                "shape": "rect",
            }
        ],
        "walls": [{"floorId": "floor-1", "points": [{"x": 0, "y": 0}, {"x": 100, "y": 0}]}],
        "aisles": [{"nodes": [{"id": "node-1", "floorId": "floor-1", "x": 10, "y": 10}], "edges": []}],
        "pois": [
            {
                "id": "poi-1",
                "floorId": "floor-1",
                "type": "checkout",
                "x": 30,
                "y": 40,
                "label": "Caisse 1",
                "checkoutKind": "selfCheckout",
                "paymentMode": "cardOnly",
                "isAccessible": True,
            }
        ],
    }

    save_response = client.put("/api/stores/1/map", json=payload)
    reload_response = client.get("/api/stores/1/map")

    assert save_response.status_code == 200
    assert reload_response.status_code == 200
    assert reload_response.json() == payload


def test_delete_store_map():
    # Quoi ?
    # Verifie la suppression d'une map de magasin.
    # Comment ?
    # On sauvegarde une map, on appelle DELETE, puis on recharge la map.
    # Pourquoi ?
    # S'assurer que la suppression remet le magasin dans un etat de map vide.
    client = create_client()
    payload = {
        "floors": [{"id": "floor-1", "name": "RDC", "order": 0}],
        "categories": [],
        "zones": [],
        "walls": [],
        "aisles": [],
        "pois": [],
    }

    client.put("/api/stores/1/map", json=payload)
    response = client.delete("/api/stores/1/map")
    reload_response = client.get("/api/stores/1/map")

    assert response.status_code == 204
    assert reload_response.json()["floors"] == []
