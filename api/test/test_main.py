import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# --------------------------------------------
from api.main import app
from api.database import get_session
# --- CONFIGURATION DE LA BASE DE TEST (SQLite en mémoire) ---
# On crée une base de données temporaire juste pour le test
engine_test = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

# Fonction pour remplacer le get_session habituel
def get_session_override():
    with Session(engine_test) as session:
        yield session

# On injecte cette dépendance dans FastAPI
app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

# mise en place d'une fausse db pour faire les tests
@pytest.fixture(name="setup_db")
def setup_db():
    # Crée les tables avant le test
    SQLModel.metadata.create_all(engine_test)
    yield
    # Supprime les tables après le test
    SQLModel.metadata.drop_all(engine_test)

    # moi, la fleche à côté de la fonction ne marche pas alors que je fais les tests avec cette commande :

    # python -m pytest api/test/test_main.py

    # ne pas oublier de se mettre dans .venv avant

    # j'ai modifié les noms des champs de certains model car il fallait que ça corresponde au nom des champs en base de donnée,
    # j'ai juste traduit les champs de l'anglais en français pas le temps de tout renommé en français
    # du coup le test, il passe, mais il y a des warning je sais, c'est juste datetime dans les model qui est deprecated,
    # je ne sais pas pourquoi, mais ce n'est pas bloquant

def test_add_product_to_cart(setup_db):
    # on récupère un panier, ça correspond au parametre "body" des fonctions
    # (faire aussi un test pour la création de panier, j'aurais dû commencer par la mais la première fonction de
    # carts.py c'était l'ajout et pas la création du panier, je n'ai pas fait gaffe) + les testes d'erreurs en mode qu'est-ce qui se passe si
    # utilisateur_id n'est pas défini et idem pour magasin_id juste, on renvoie une erreur 500 aux lieux de 200

    cart_payload = {
        "utilisateur_id": 1,
        "magasin_id": 1
    }
    cart_resp = client.post("/cart/", json=cart_payload)

# Si on veut débugger une erreur, on rentre dans tout ce qui n'est pas un code 200 et on print l'erreur puis on sort dans de l'assert

#    if cart_resp.status_code != 200:
#        print(cart_resp.json())
#    assert cart_resp.status_code == 200
    new_cart_id = cart_resp.json()["id"]

# le parametre "body" de la fonction qui est le produit à ajouter dans le panier
    product_payload = {
        "panier_id": new_cart_id,
        "produit_id": 123,
        "quantite": 2
    }

    # On veut acceder à l'url avec le json en parametre qui correspond au parametre "body" de la fonction appelé
    response = client.post("/cart/product/", json=product_payload)

    #if response.status_code != 200:
    #    print(f"Détail erreur produit: {response.json()}")
    #assert response.status_code == 200

    assert response.status_code == 200
    data = response.json()
    assert data["panier_id"] == new_cart_id