from sqlmodel import create_engine, Session, SQLModel

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_DB = "caddiescan"
POSTGRES_HOST = "localhost"  
POSTGRES_PORT = 5432

postgres_url = f"postgresql://neondb_owner:npg_prjD0ViwuL3n@ep-silent-band-al1g8emv-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(postgres_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
