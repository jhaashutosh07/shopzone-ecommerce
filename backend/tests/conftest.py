import os
import sys

# Test environment must be set before any app module is imported,
# because settings are cached at import time.
TEST_DB = os.path.join(os.path.dirname(__file__), "test_engine.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["DEMO_MERCHANT_EMAIL"] = "demo-merchant@shopzone.test"
os.environ["DEMO_MERCHANT_PASSWORD"] = "demo1234"
os.environ["DEMO_API_KEY"] = "rpe_test_demo_key_000000000000000000"
os.environ["SECRET_KEY"] = "test-secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    from app.main import app
    from app.database import engine

    # Context manager runs the lifespan (bootstrap: schema, model, demo merchant)
    with TestClient(app) as test_client:
        yield test_client

    engine.dispose()
    try:
        os.remove(TEST_DB)
    except OSError:
        pass  # Windows may briefly keep the file locked
