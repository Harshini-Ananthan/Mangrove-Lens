import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.utils.config import settings

# Ensure data directory exists for SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite:///")
if is_sqlite:
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path.startswith("data/"):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
