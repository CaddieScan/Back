# CaddieScan Frontend API

Base URL locale:

```text
http://localhost:8000/api
```

Commande de lancement:

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Variables indispensables actuellement:

```text
Aucune variable d'environnement n'est lue par le code actuel.
La base PostgreSQL attendue est:
postgresql://postgres:postgres@localhost:5432/caddiescan
```

## Magasins

Table utilisee en base: `magasin`.

Champs retournes:

```json
{
  "id": 1,
  "name": "Carrefour Centre",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

Routes:

```text
GET    /api/stores
GET    /api/stores/{id}
POST   /api/stores
PUT    /api/stores/{id}
DELETE /api/stores/{id}
```

Body `POST /api/stores`:

```json
{
  "name": "Carrefour Centre",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

Body `PUT /api/stores/{id}`:

```json
{
  "name": "Carrefour Centre",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

Tous les champs du `PUT` sont optionnels.

## Produits

Tables utilisees en base: `produit`, `rayon`, `etage`.

Le champ `id` retourne `produit.code_barre`.
Le champ `storeId` est deduit par la relation `produit -> rayon -> magasin`.
Les champs `quantity` et `unit` sont conserves pour compatibilite frontend, mais ils ne sont pas stockes dans le schema SQL actuel.

Champs retournes:

```json
{
  "id": 1,
  "storeId": 1,
  "name": "Lait demi-ecreme",
  "category": "Produits laitiers",
  "price": 1.25,
  "quantity": 1,
  "unit": "L",
  "barcode": "1234567890123",
  "imageAssetPath": "/images/lait.png",
  "imageUrl": "/images/lait.png"
}
```

Routes:

```text
GET    /api/stores/{storeId}/products
GET    /api/stores/{storeId}/products/{productId}
POST   /api/stores/{storeId}/products
POST   /api/stores/{storeId}/products/bulk
PUT    /api/stores/{storeId}/products/{productId}
DELETE /api/stores/{storeId}/products/{productId}
```

Body `POST /api/stores/{storeId}/products`:

```json
{
  "name": "Lait demi-ecreme",
  "category": "Produits laitiers",
  "price": 1.25,
  "quantity": 1,
  "unit": "L",
  "barcode": "1234567890123",
  "imageAssetPath": "/images/lait.png"
}
```

Body `POST /api/stores/{storeId}/products/bulk`:

```json
{
  "products": [
    {
      "name": "Lait demi-ecreme",
      "category": "Produits laitiers",
      "price": 1.25,
      "quantity": 1,
      "unit": "L",
      "barcode": "1234567890123",
      "imageAssetPath": "/images/lait.png"
    }
  ]
}
```

Body `PUT /api/stores/{storeId}/products/{productId}`:

```json
{
  "name": "Lait demi-ecreme",
  "category": "Produits laitiers",
  "price": 1.25,
  "quantity": 1,
  "unit": "L",
  "barcode": "1234567890123",
  "imageAssetPath": "/images/lait.png"
}
```

Tous les champs du `PUT` sont optionnels.

## Carte Magasin

Table utilisee en base: `carte_magasin_donnee`.
Cette table est creee automatiquement si elle n'existe pas encore, avec des noms de colonnes en francais: `magasin_id`, `donnees`, `date_heure_modification`.

Routes:

```text
GET /api/stores/{storeId}/map
PUT /api/stores/{storeId}/map
DELETE /api/stores/{storeId}/map
```

Si aucune carte n'existe encore, `GET` retourne une carte vide:

```json
{
  "floors": [],
  "categories": [],
  "zones": [],
  "walls": [],
  "aisles": [],
  "pois": []
}
```

Body et retour `PUT /api/stores/{storeId}/map`:

```json
{
  "floors": [
    {
      "id": "floor-1",
      "name": "RDC",
      "order": 0
    }
  ],
  "categories": [
    {
      "id": "cat-1",
      "name": "Boissons",
      "color": "#3b82f6"
    }
  ],
  "zones": [
    {
      "id": "zone-1",
      "floorId": "floor-1",
      "name": "Rayon boissons",
      "categoryId": "cat-1",
      "x": 10,
      "y": 20,
      "w": 120,
      "h": 80,
      "shape": "rect"
    }
  ],
  "walls": [
    {
      "floorId": "floor-1",
      "points": [
        { "x": 0, "y": 0 },
        { "x": 100, "y": 0 }
      ]
    }
  ],
  "aisles": [
    {
      "nodes": [
        {
          "id": "node-1",
          "floorId": "floor-1",
          "x": 10,
          "y": 10
        }
      ],
      "edges": []
    }
  ],
  "pois": [
    {
      "id": "poi-1",
      "floorId": "floor-1",
      "type": "entry",
      "x": 5,
      "y": 5,
      "label": "Entree",
      "checkoutKind": "selfCheckout",
      "paymentMode": "cardOnly",
      "isAccessible": true
    }
  ]
}
```
