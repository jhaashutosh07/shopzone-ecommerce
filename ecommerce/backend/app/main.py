from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect

from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, products, cart, orders, returns, reviews, wishlist

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Columns added after the initial release; applied idempotently on boot
SCHEMA_UPGRADES = [
    ("return_requests", "engine_explanation", "TEXT"),
    ("products", "details", "TEXT"),
]


def ensure_schema():
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table, column, col_type in SCHEMA_UPGRADES:
            if table not in inspector.get_table_names():
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            if column not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
                print(f"Schema upgrade: added {table}.{column}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_schema()
    if settings.auto_seed:
        from app.services.seed import seed_database
        db = SessionLocal()
        try:
            result = seed_database(db)
            print(f"Auto-seed: {result['message']}")
        finally:
            db.close()
    if settings.import_catalog:
        from app.services.importer import import_catalog
        db = SessionLocal()
        try:
            result = import_catalog(db)
            print(f"Catalog import: {result['message']}")
        finally:
            db.close()
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Full-featured E-commerce API with Return Policy Engine integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(cart.router, prefix=settings.api_prefix)
app.include_router(orders.router, prefix=settings.api_prefix)
app.include_router(returns.router, prefix=settings.api_prefix)
app.include_router(reviews.router, prefix=settings.api_prefix)
app.include_router(wishlist.router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "api_prefix": settings.api_prefix
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Seed data endpoint for development
@app.post("/api/v1/seed")
def seed_database_endpoint():
    """Seed database with sample data for development."""
    from app.services.seed import seed_database

    db = SessionLocal()
    try:
        return seed_database(db)
    finally:
        db.close()


@app.post("/api/v1/catalog/import")
def import_catalog_endpoint():
    """Import real product listings from the web catalog (idempotent)."""
    from app.services.importer import import_catalog

    db = SessionLocal()
    try:
        return import_catalog(db)
    finally:
        db.close()
