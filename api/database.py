from pathlib import Path
from sqlmodel import create_engine, Session, SQLModel

# Build sqlite path relative to this file to avoid cwd issues
BASE_DIR = Path(__file__).resolve().parent
sqlite_file_name = BASE_DIR.parent / "db" / "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
