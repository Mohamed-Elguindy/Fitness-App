from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# If using Neon (Postgres) we use standard postgresql URL. If using sqlite, check_same_thread=False is needed.
connect_args = {"check_same_thread": False} if settings.NEON_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.NEON_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
