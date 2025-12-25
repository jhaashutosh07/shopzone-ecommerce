from app.routers.auth import router as auth_router
from app.routers.scoring import router as scoring_router
from app.routers.returns import router as returns_router
from app.routers.buyers import router as buyers_router
from app.routers.products import router as products_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "scoring_router",
    "returns_router",
    "buyers_router",
    "products_router",
    "dashboard_router",
]
