-- =========================
-- SEED MAGASIN COMPLET
-- =========================

BEGIN;

ALTER TABLE produit
ALTER COLUMN code_barre TYPE BIGINT;


-- 1️⃣ ROLE
INSERT INTO role (id, libelle, archivage)
VALUES (1, 'ADMIN', false);

-- 2️⃣ MAGASIN
INSERT INTO magasin (id, libelle, longitude, latitude, chemin_absolut_logo)
VALUES (
  1,
  'Supermarché Test',
  2.3522,
  48.8566,
  '/logos/magasin_test.png'
);

-- 3️⃣ UTILISATEUR
INSERT INTO utilisateur (id, role_id, magasin_id, nom, prenom, mail, mdp)
VALUES (
  1,
  1,
  1,
  'Doe',
  'John',
  'john.doe@test.com',
  'hashed_password'
);

-- 4️⃣ ETAGE
INSERT INTO etage (id, magasin_id, numero)
VALUES (1, 1, 0);

-- 5️⃣ RAYON
INSERT INTO rayon (
  id, magasin_id, etage_id, libelle,
  point1_x, point1_y, point2_x, point2_y
)
VALUES (
  1, 1, 1, 'Boissons',
  0.0, 0.0, 10.0, 5.0
);

-- 6️⃣ PROMOTION
INSERT INTO promotion (
  id, magasin_id, libelle,
  date_heure_debut, date_heure_fin,
  mode_promotion,
  quantite_acheter, quantite_offert,
  pourcentage_reduction, reduction_fixe,
  caniotte_immediate
)
VALUES (
  1,
  1,
  'Promo boissons',
  NOW(),
  NOW() + INTERVAL '30 days',
  'POURCENTAGE',
  NULL,
  NULL,
  10.0,
  NULL,
  false
);

-- 7️⃣ PRODUIT
INSERT INTO produit (
  code_barre, rayon_id, promotion_id,
  libelle, image, prix
)
VALUES (
  1234567890123,
  1,
  1,
  'Bouteille d’eau 1.5L',
  '/images/eau.png',
  1.25
);

COMMIT;
