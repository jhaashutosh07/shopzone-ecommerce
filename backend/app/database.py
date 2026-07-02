from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

if settings.database_url.startswith("sqlite"):
    # SQLite (tests / lightweight local runs) doesn't support pooling args
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
