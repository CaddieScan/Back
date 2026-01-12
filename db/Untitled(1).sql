CREATE TABLE "utilisateur" (
  "id" integer PRIMARY KEY,
  "role_id" integer NOT NULL,
  "magasin_id" integer,
  "nom" text NOT NULL,
  "prenom" text NOT NULL,
  "mail" text NOT NULL,
  "mdp" text NOT NULL
);

CREATE TABLE "role" (
  "id" integer PRIMARY KEY,
  "libelle" text NOT NULL,
  "archivage" bool NOT NULL
);

CREATE TABLE "magasin" (
  "id" integer PRIMARY KEY,
  "libelle" text NOT NULL,
  "longitude" float,
  "latitude" float,
  "chemin_absolut_logo" text NOT NULL
);

CREATE TABLE "magasin_favori" (
  "id" integer PRIMARY KEY,
  "utilisateur_id" integer NOT NULL,
  "magasin_id" integer NOT NULL
);

CREATE TABLE "carte_fidelite" (
  "id" integer PRIMARY KEY,
  "utilisateur_id" integer NOT NULL,
  "magasin_id" integer NOT NULL,
  "code_barre" int NOT NULL
);

CREATE TABLE "panier" (
  "id" integer PRIMARY KEY,
  "utilisateur_id" integer NOT NULL,
  "magasin_id" integer NOT NULL,
  "code_barre" integer NOT NULL,
  "total_ttc" integer NOT NULL,
  "date_heure_creation" timestamp NOT NULL
);

CREATE TABLE "rayon" (
  "id" integer PRIMARY KEY,
  "magasin_id" integer NOT NULL,
  "etage_id" integer NOT NULL,
  "libelle" text NOT NULL,
  "point1_x" float NOT NULL,
  "point1_y" float NOT NULL,
  "point2_x" float NOT NULL,
  "point2_y" float NOT NULL
);

CREATE TABLE "produit" (
  "code_barre" integer PRIMARY KEY,
  "rayon_id" integer NOT NULL,
  "promotion_id" integer,
  "libelle" text NOT NULL,
  "image" text,
  "prix" float NOT NULL
);

CREATE TABLE "carte_magasin" (
  "id" integer PRIMARY KEY,
  "magasin_id" integer NOT NULL,
  "rayon_id" integer NOT NULL,
  "chemin_asbolut" text NOT NULL
);

CREATE TABLE "scan_panier" (
  "id" integer PRIMARY KEY,
  "panier_id" integer NOT NULL,
  "produit_id" integer NOT NULL,
  "libelle" text NOT NULL,
  "quantite" integer NOT NULL,
  "date_heure_creation" timestamp NOT NULL
);

CREATE TABLE "etage" (
  "id" integer PRIMARY KEY,
  "magasin_id" integer NOT NULL,
  "numero" integer NOT NULL
);

CREATE TABLE "promotion" (
  "id" integer PRIMARY KEY,
  "magasin_id" integer NOT NULL,
  "libelle" text NOT NULL,
  "date_heure_debut" timestamp NOT NULL,
  "date_heure_fin" timestamp NOT NULL,
  "mode_promotion" text NOT NULL,
  "quantite_acheter" integer,
  "quantite_offert" integer,
  "pourcentage_reduction" float,
  "reduction_fixe" float,
  "caniotte_immediate" bool
);

ALTER TABLE "magasin_favori" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "magasin_favori" ADD FOREIGN KEY ("utilisateur_id") REFERENCES "utilisateur" ("id");

ALTER TABLE "utilisateur" ADD FOREIGN KEY ("role_id") REFERENCES "role" ("id");

ALTER TABLE "carte_fidelite" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "carte_fidelite" ADD FOREIGN KEY ("utilisateur_id") REFERENCES "utilisateur" ("id");

ALTER TABLE "rayon" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "produit" ADD FOREIGN KEY ("rayon_id") REFERENCES "rayon" ("id");

ALTER TABLE "panier" ADD FOREIGN KEY ("utilisateur_id") REFERENCES "utilisateur" ("id");

ALTER TABLE "panier" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "utilisateur" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "scan_panier" ADD FOREIGN KEY ("panier_id") REFERENCES "panier" ("id");

ALTER TABLE "carte_magasin" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "carte_magasin" ADD FOREIGN KEY ("rayon_id") REFERENCES "rayon" ("id");

ALTER TABLE "scan_panier" ADD FOREIGN KEY ("produit_id") REFERENCES "produit" ("code_barre");

ALTER TABLE "etage" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");

ALTER TABLE "rayon" ADD FOREIGN KEY ("etage_id") REFERENCES "etage" ("id");

ALTER TABLE "produit" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotion" ("id");

ALTER TABLE "promotion" ADD FOREIGN KEY ("magasin_id") REFERENCES "magasin" ("id");
