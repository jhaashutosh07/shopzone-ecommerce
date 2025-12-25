from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.routers import (
    auth_router,
    scoring_router,
    returns_router,
    buyers_router,
    products_router,
    dashboard_router,
)

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
## Dynamic Return Policy Engine API

A merchant-facing API for intelligent return eligibility scoring using ML-based fraud detection.

### Features
- **ML-Powered Scoring**: Get return eligibility scores based on buyer behavior, product attributes, and request context
- **Risk Detection**: Automatic detection of fraudulent return patterns
- **Merchant Dashboard**: Analytics and return request management
- **Flexible Integration**: Simple REST API with API key authentication

### Authentication
- **Dashboard**: JWT tokens via `/api/v1/auth/login`
- **API Integration**: API keys via `X-API-Key` header

### Quick Start
1. Register a merchant account
2. Generate an API key
3. Start scoring return requests!
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(scoring_router, prefix=settings.api_v1_prefix)
app.include_router(returns_router, prefix=settings.api_v1_prefix)
app.include_router(buyers_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(dashboard_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
