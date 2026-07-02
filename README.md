# ShopZone — E-commerce Platform with an Explainable ML Return-Fraud Engine

A full-stack e-commerce platform (storefront + merchant dashboard) built around a
**Return Policy Engine**: an ML risk-decisioning service that scores every return
request in real time, explains its decision feature-by-feature, learns from merchant
overrides, and monitors its own data drift.

Return fraud costs Indian e-commerce an estimated 2-3% of GMV. Most platforms answer
with blanket policies that punish honest customers. This project answers with
per-request decisions: a 48-order loyal customer gets instant approval; a 12-day-old
account with 5 returns in 8 orders gets auto-denied — and both can see exactly why.

## Live demo

| | URL | Login |
|---|-----|-------|
| 🛒 Storefront | https://shopzone-store.vercel.app | `demo.trusted@shopzone.com` or `demo.risky@shopzone.com` / `demo1234` |
| 📊 Merchant dashboard | https://shopzone-dashboard.vercel.app | `demo-merchant@shopzone.com` / `demo1234` |
| 🛡 Engine API docs | https://ashutosh2002-shopzone-rpe.hf.space/docs | API key auth |
| 🧾 Store API docs | https://ashutosh2002-shopzone-api.hf.space/docs | JWT auth |

Backends run on Hugging Face Spaces (free tier): the first request after idle can
take ~1 min while the Space wakes and the engine retrains its model. Data is
ephemeral there — the system re-provisions itself (model, demo merchant, seeded
store) on every restart, which is itself part of the demo.

## One-command demo

```bash
docker compose up -d --build
```

Everything self-provisions: the engine trains its initial model, registers it,
creates the demo merchant + API key, and the store seeds its catalog, demo buyers,
and delivered orders. No manual setup steps.

| URL | What | Login |
|-----|------|-------|
| http://localhost:3001 | ShopZone storefront | see demo accounts below |
| http://localhost:3000 | Merchant dashboard | `demo-merchant@shopzone.com` / `demo1234` |
| http://localhost:8000/docs | Return Policy Engine API | API key auth |
| http://localhost:8001/docs | Store API | JWT auth |

### The 90-second demo script

1. Log in to the storefront as **`demo.risky@shopzone.com`** / `demo1234`
   (new account, 5 returns in 8 orders). Open **Orders**, pick the Smart Fitness
   Watch, request a return with reason *Changed my mind*.
   → **Auto-denied in real time.** The detail page shows the score (≈0/100) and
   the per-feature breakdown: buyer return rate −47 pts, no reviews −39 pts,
   account age −21 pts.
2. Log out, log in as **`demo.trusted@shopzone.com`** / `demo1234`
   (48 orders, 1 return, 500-day-old account). Return the jeans for *Size issue*.
   → **Auto-approved** (score ≈90/100) with the positive contributions shown.
3. Open the merchant dashboard → **Returns** to see both decisions with risk
   flags and the "Why this decision" waterfall. Override any REVIEW decision —
   that becomes labeled training data.
4. Dashboard → **Models**: hit **Retrain from feedback**. A new model version is
   trained with your overrides as ground truth, registered with its metrics, and
   hot-swapped into serving. The **Data Drift** panel shows per-feature PSI of
   live traffic vs. the training distribution.

## Architecture

```
┌──────────────────┐         ┌──────────────────┐
│   Storefront     │────────▶│   Store API       │──────────────┐
│   Next.js :3001  │         │   FastAPI :8001   │              │ X-API-Key
└──────────────────┘         │   (orders, cart,  │              ▼
                             │    returns, ...)  │   ┌──────────────────────┐
┌──────────────────┐         └────────┬─────────┘   │  Return Policy Engine │
│ Merchant         │                  │             │  FastAPI :8000        │
│ Dashboard        │──────────────────┼────────────▶│  • scoring + flags    │
│ Next.js :3000    │   JWT            │             │  • explainability     │
└──────────────────┘                  ▼             │  • model registry     │
                             ┌─────────────┐        │  • drift monitor (PSI)│
                             │ PostgreSQL  │        └──────────┬───────────┘
                             │ (store)     │                   ▼
                             └─────────────┘        ┌─────────────┐
                                                    │ PostgreSQL  │
                                                    │ (engine)    │
                                                    └─────────────┘
```

The engine is a standalone multi-tenant SaaS-style service: any storefront can
integrate via three endpoints (`/buyers/sync`, `/products/sync`, `/score`) with an
API key. ShopZone is the reference integration — the store syncs buyer/product
stats before scoring and auto-applies APPROVE/DENY recommendations.

## What makes the ML layer more than a `model.predict()`

**Explainable decisions.** Every score ships with per-feature contributions
computed by interventional ablation against training-set baselines: each feature
is replaced by its training median and the probability shift is attributed to it,
in score points. Both the merchant dashboard and the customer-facing return page
render the waterfall. No black-box denials.

**Feedback loop (human-in-the-loop retraining).** When a merchant overrides a
system decision, the request's feature snapshot + the human decision become a
labeled sample. `POST /models/retrain` mixes this ground truth into training at
elevated weight, evaluates, registers a new version in the model registry
(Postgres-backed, with metrics), and hot-swaps serving — no restart.

**Model registry + versioned serving.** Every trained model is stored with its
accuracy / precision / recall / F1 / ROC-AUC, sample counts, and timestamps.
Each scored request records which model version decided it, so any historical
decision is reproducible.

**Drift monitoring.** The training feature distributions travel with the model
bundle. The `/models/drift` endpoint computes Population Stability Index per
feature over recent live traffic (PSI > 0.25 = drifted) and the dashboard
surfaces it — the standard "is my model going stale" signal used in production
risk systems.

**Hybrid scoring.** The gradient-boosting score is combined with deterministic
risk flags (return window, velocity, account age, order value) and
merchant-configurable thresholds (auto-approve / fraud) — ML informs, policy
decides. Falls back to a transparent rules engine if no model is available.

**Honest evaluation.** The synthetic training data (modeled on Flipkart/Amazon
return patterns: category return rates, buyer personas, seasonal effects)
deliberately overlaps fraud and legitimate behavior and injects ~4% label noise,
so reported metrics (~87% accuracy, ROC-AUC ~0.78) reflect a learnable-but-hard
problem instead of leaking the label. Swapping in a real dataset (e.g. Olist)
only requires implementing one loader function.

### ML feature set (15 features)

| Group | Features |
|-------|----------|
| Buyer history | return rate, total orders/returns, avg review score, account age, lifetime spend |
| Product | category risk, product return rate, price, price tier |
| Request context | days since order, order amount, return reason, hour, day of week |

## API quick reference (engine)

```bash
# Score a return request
curl -X POST http://localhost:8000/api/v1/score \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{
    "buyer_id": "buyer_123", "product_id": "prod_456", "order_id": "order_789",
    "order_date": "2026-06-25T00:00:00Z", "order_amount": 1999,
    "return_reason": "size_issue"
  }'
```

```jsonc
// Response (abridged)
{
  "score": 89.7, "risk_level": "low", "recommendation": "APPROVE",
  "confidence": 0.93, "model_version": 3,
  "risk_flags": [],
  "explanation": [
    {"label": "Return reason", "value": "size_issue", "contribution": 15.3, "direction": "positive"},
    {"label": "Buyer review score", "value": "4.80", "contribution": 0.4, "direction": "positive"}
  ]
}
```

Other endpoints: `POST /buyers/sync`, `POST /products/sync`, `GET/PUT /returns`,
`GET /models`, `POST /models/retrain`, `GET /models/drift`, `GET /dashboard/stats`.
Interactive docs at `/docs` on both services.

## Running tests

```bash
cd backend
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows
.venv/Scripts/python -m pytest tests/ -q
```

The suite covers the full loop end-to-end against a live app instance:
bootstrap provisioning, trusted-vs-risky scoring contrast, explanation payloads,
merchant override → retrain → version activation, and the drift report.

## Local development (without Docker)

```bash
# Terminal 1 - engine (trains a model on first boot)
cd backend && pip install -r requirements.txt
DEMO_MERCHANT_EMAIL=demo-merchant@shopzone.com DEMO_API_KEY=rpe_dev_key_123 \
  uvicorn app.main:app --port 8000

# Terminal 2 - store API (auto-seeds demo data)
cd ecommerce/backend && pip install -r requirements.txt
AUTO_SEED=true RETURN_ENGINE_URL=http://localhost:8000/api/v1 \
  RETURN_ENGINE_API_KEY=rpe_dev_key_123 uvicorn app.main:app --port 8001

# Terminals 3 & 4 - frontends
cd dashboard && npm install && npm run dev            # :3000
cd ecommerce/frontend && npm install && npm run dev   # :3001
```

SQLite works out of the box for quick local runs
(`DATABASE_URL=sqlite:///./dev.db`); Postgres is used in Docker/production.

## Deployment

`render.yaml` deploys both APIs (engine + store) and a free Postgres to
[Render](https://render.com); point the two Next.js apps at them from Vercel with
`NEXT_PUBLIC_API_URL`. Set matching `DEMO_API_KEY` / `RETURN_ENGINE_API_KEY`
values so the store-to-engine integration provisions itself, exactly like the
compose setup.

> Checkout uses simulated payments (COD/UPI/card selection without a gateway) —
> the focus of this project is the returns/risk pipeline, not payment processing.

## Project structure

```
├── backend/                  # Return Policy Engine (FastAPI + scikit-learn)
│   ├── app/ml/               # training, prediction, explainability, drift
│   ├── app/routers/          # score, returns, buyers, products, models, auth
│   ├── app/services/         # scoring engine, bootstrap, auth
│   └── tests/                # end-to-end API tests
├── dashboard/                # Merchant dashboard (Next.js)
├── ecommerce/
│   ├── backend/              # Store API (FastAPI): cart, orders, returns, reviews
│   └── frontend/             # Storefront (Next.js)
├── docker-compose.yml        # full stack, one command
└── render.yaml               # cloud deployment blueprint
```

## License

MIT
