CREATE TABLE IF NOT EXISTS carte_magasin_donnee (
  magasin_id integer PRIMARY KEY REFERENCES magasin(id),
  donnees jsonb NOT NULL,
  date_heure_modification timestamp NOT NULL
);
