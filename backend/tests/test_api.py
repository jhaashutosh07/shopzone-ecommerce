"""End-to-end API tests: bootstrap, scoring, explainability, feedback
retraining, model registry, and drift monitoring."""
from datetime import datetime, timedelta

API_KEY = "rpe_test_demo_key_000000000000000000"
HEADERS = {"X-API-Key": API_KEY}


def _login(client) -> dict:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "demo-merchant@shopzone.test", "password": "demo1234"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _sync_buyer(client, buyer_id, orders, returns, review_score, spend, age_days):
    resp = client.post("/api/v1/buyers/sync", headers=HEADERS, json={
        "buyers": [{
            "external_buyer_id": buyer_id,
            "total_orders": orders,
            "total_returns": returns,
            "total_reviews": max(orders // 2, 0),
            "avg_review_score": review_score,
            "total_spend": spend,
            "account_created_at": (datetime.utcnow() - timedelta(days=age_days)).isoformat(),
        }]
    })
    assert resp.status_code == 200, resp.text


def _score(client, buyer_id, product_id, amount, reason, days_ago=5):
    resp = client.post("/api/v1/score", headers=HEADERS, json={
        "buyer_id": buyer_id,
        "product_id": product_id,
        "order_id": f"order-{buyer_id}-{product_id}",
        "order_date": (datetime.utcnow() - timedelta(days=days_ago)).isoformat(),
        "order_amount": amount,
        "return_reason": reason,
    })
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_health(client):
    assert client.get("/health").json()["status"] == "healthy"


def test_bootstrap_provisioned_model_and_merchant(client):
    """Startup must yield a working API key and a registered model."""
    headers = _login(client)
    resp = client.get("/api/v1/models", headers=headers)
    assert resp.status_code == 200, resp.text
    models = resp.json()
    assert len(models) >= 1
    assert any(m["is_active"] for m in models)
    active = next(m for m in models if m["is_active"])
    assert active["roc_auc"] is not None


def test_trusted_vs_risky_buyer_scores(client):
    """The whole pitch: history changes the decision, and the decision
    comes with an explanation."""
    _sync_buyer(client, "trusted-1", orders=50, returns=1,
                review_score=4.8, spend=200000, age_days=500)
    _sync_buyer(client, "risky-1", orders=8, returns=5,
                review_score=2.0, spend=30000, age_days=12)

    trusted = _score(client, "trusted-1", "prod-jeans", 1999, "size_issue", days_ago=4)
    risky = _score(client, "risky-1", "prod-watch", 7999, "changed_mind", days_ago=6)

    assert trusted["score"] > risky["score"]
    assert trusted["recommendation"] in ("APPROVE", "REVIEW")
    assert risky["recommendation"] in ("DENY", "REVIEW")
    assert risky["risk_flags"], "risky buyer should trip risk flags"

    # Explainability: every scored decision ships its top contributions
    for result in (trusted, risky):
        assert result["explanation"], "explanation must not be empty"
        top = result["explanation"][0]
        assert {"feature", "label", "value", "contribution", "direction"} <= set(top)
        assert result["model_version"] is not None

    # The risky buyer's return rate should push the score down
    risky_features = {c["feature"]: c for c in risky["explanation"]}
    assert any(
        c["direction"] == "negative" for c in risky_features.values()
    ), "risky decision should have negative contributors"


def test_return_detail_includes_explanation(client):
    result = _score(client, "trusted-1", "prod-jeans", 1999, "size_issue")
    resp = client.get(f"/api/v1/returns/{result['request_id']}", headers=HEADERS)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["explanation"]
    assert body["risk_flags"] is not None


def test_feedback_loop_retrain_and_registry(client):
    """Merchant override becomes ground truth; retrain bumps the version."""
    headers = _login(client)

    result = _score(client, "risky-1", "prod-headphones", 4999, "changed_mind")
    request_id = result["request_id"]

    # Merchant overrides the system decision -> labeled feedback
    resp = client.put(
        f"/api/v1/returns/{request_id}",
        headers=headers,
        json={"decision": "approved"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["decided_by"] not in (None, "system")

    before = client.get("/api/v1/models", headers=headers).json()
    max_version_before = max(m["version"] for m in before)

    resp = client.post("/api/v1/models/retrain", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["version"] == max_version_before + 1
    assert body["feedback_samples"] >= 1
    assert body["activated"] is True

    after = client.get("/api/v1/models", headers=headers).json()
    active = next(m for m in after if m["is_active"])
    assert active["version"] == body["version"]
    assert active["feedback_samples"] >= 1

    # Serving layer hot-swapped to the new version
    rescored = _score(client, "risky-1", "prod-watch", 7999, "changed_mind")
    assert rescored["model_version"] == body["version"]


def test_drift_report(client):
    headers = _login(client)

    # Not enough traffic yet -> insufficient_data (never a 500)
    resp = client.get("/api/v1/models/drift", headers=headers)
    assert resp.status_code == 200, resp.text

    # Generate enough scored traffic for a real report
    for i in range(35):
        _sync_buyer(client, f"bulk-{i}", orders=10 + i, returns=i % 4,
                    review_score=3.0 + (i % 3) * 0.5, spend=5000 + i * 100,
                    age_days=30 + i * 10)
        _score(client, f"bulk-{i}", f"prod-{i % 5}", 500 + i * 50,
               "size_issue" if i % 2 else "defective", days_ago=(i % 20) + 1)

    resp = client.get("/api/v1/models/drift", headers=headers)
    assert resp.status_code == 200, resp.text
    report = resp.json()
    assert report["samples_analyzed"] >= 30
    assert report["overall_status"] in ("stable", "moderate", "drifted")
    assert report["features"], "per-feature PSI list must not be empty"
    for feat in report["features"]:
        assert feat["psi"] >= 0
        assert feat["status"] in ("stable", "moderate", "drifted")
