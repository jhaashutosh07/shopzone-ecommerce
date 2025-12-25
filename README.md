# Dynamic Return Policy Engine

An ML-powered return eligibility scoring system for e-commerce merchants. This system helps merchants reduce return fraud while maintaining customer trust through intelligent, data-driven return decisions.

## Features

- **ML-Powered Scoring**: Gradient Boosting model analyzes buyer behavior, product attributes, and request context
- **Risk Detection**: Automatic detection of fraudulent return patterns with detailed risk flags
- **Configurable Thresholds**: Merchants can set auto-approve and auto-deny score thresholds
- **Real-time API**: Simple REST API for seamless integration with any e-commerce platform
- **Merchant Dashboard**: Analytics, return management, and policy configuration UI

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Merchant UI   │────▶│   FastAPI       │────▶│   PostgreSQL    │
│   (Next.js)     │     │   Backend       │     │   Database      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────┴────────┐
                        │   ML Scoring    │
                        │   Engine        │
                        └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. Clone the repository:
```bash
cd return-policy-engine
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
   - Dashboard: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - API: http://localhost:8000/api/v1

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start PostgreSQL (or use Docker)
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=return_engine -p 5432:5432 postgres:15-alpine

# Train the ML model (optional - will use rules-based fallback)
python -m app.ml.train

# Run the server
uvicorn app.main:app --reload
```

#### Dashboard

```bash
cd dashboard

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local

# Run development server
npm run dev
```

## API Usage

### Authentication

The API uses API keys for authentication. Generate one from the dashboard or via API.

Include the key in requests:
```
X-API-Key: rpe_your_api_key_here
```

### Calculate Return Score

```bash
curl -X POST "http://localhost:8000/api/v1/score" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyer_id": "buyer_123",
    "product_id": "prod_456",
    "order_id": "order_789",
    "order_date": "2024-01-15T00:00:00Z",
    "order_amount": 99.99,
    "return_reason": "size_issue"
  }'
```

Response:
```json
{
  "score": 78,
  "risk_level": "low",
  "recommendation": "APPROVE",
  "risk_flags": [],
  "return_window_days": 30,
  "confidence": 0.92,
  "buyer_return_rate": 5.2,
  "days_since_order": 12,
  "within_return_window": true,
  "request_id": "uuid-here"
}
```

### Sync Buyer Data

```bash
curl -X POST "http://localhost:8000/api/v1/buyers/sync" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "buyers": [
      {
        "external_buyer_id": "buyer_123",
        "total_orders": 25,
        "total_returns": 2,
        "avg_review_score": 4.5,
        "total_spend": 1500.00
      }
    ]
  }'
```

### Sync Product Catalog

```bash
curl -X POST "http://localhost:8000/api/v1/products/sync" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "external_product_id": "prod_456",
        "name": "Blue T-Shirt",
        "category": "clothing",
        "price": 29.99
      }
    ]
  }'
```

## ML Model

### Features Used

**Buyer Behavior:**
- Return rate (returns/orders)
- Total orders and returns
- Average review score
- Account age
- Total spend

**Product Attributes:**
- Category risk score
- Price tier
- Product return rate

**Request Context:**
- Days since order
- Order amount
- Return reason
- Request timing

### Risk Flags

The system detects various risk indicators:
- `HIGH_RETURN_RATE`: Buyer returns >30% of orders
- `NEW_ACCOUNT`: Account <30 days old
- `OUTSIDE_RETURN_WINDOW`: Request past return deadline
- `MULTIPLE_RECENT_RETURNS`: 3+ returns in current month
- `HIGH_VALUE_ITEM`: Order >$500
- And more...

## Configuration

### Environment Variables

**Backend:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (change in production!)
- `HIGH_RISK_THRESHOLD`: Score below which returns are denied (default: 30)
- `MEDIUM_RISK_THRESHOLD`: Score above which returns are low risk (default: 60)

**Dashboard:**
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Project Structure

```
return-policy-engine/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB connection
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── ml/                  # ML model code
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   ├── lib/                     # Utilities
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

MIT
