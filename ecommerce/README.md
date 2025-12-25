# ShopZone E-commerce Platform

A full-featured e-commerce platform integrated with the Return Policy Engine for intelligent return management.

## Features

### Buyer Features
- **Product Browsing**: Search, filter, and browse products by category
- **Shopping Cart**: Add/remove items, update quantities
- **Checkout**: Multiple payment methods, address management
- **Order Management**: View orders, track status, cancel orders
- **Returns**: Request returns with AI-powered eligibility scoring
- **Reviews**: Leave product reviews and ratings
- **Wishlist**: Save products for later

### Seller Features
- **Product Management**: Add, edit, delete products
- **Order Management**: View and update order status
- **Return Management**: Review return requests, approve/deny, process refunds

### Return Policy Engine Integration
- Real-time return eligibility scoring
- Risk flag detection (high return rate, new account, etc.)
- Auto-approve/deny based on AI recommendations
- Buyer data sync for better predictions

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Authentication**: JWT tokens
- **State Management**: Zustand

## Quick Start

### Using Docker Compose

```bash
cd ecommerce
docker-compose up --build
```

This starts:
- PostgreSQL database on port 5433
- Backend API on http://localhost:8001
- Frontend on http://localhost:3001

### Manual Setup

#### Backend

```bash
cd ecommerce/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run the server
uvicorn app.main:app --reload --port 8001
```

#### Frontend

```bash
cd ecommerce/frontend

# Install dependencies
npm install

# Set environment variables
cp .env.local.example .env.local

# Run development server
npm run dev
```

## Seed Data

After starting the application, seed the database with sample data:

```bash
curl -X POST http://localhost:8001/api/v1/seed
```

This creates:
- Admin user: admin@shopzone.com / admin123
- Seller user: seller@shopzone.com / seller123
- Buyer user: buyer@example.com / buyer123
- 10 sample products

## Integration with Return Policy Engine

### Configuration

Set the following environment variables:

```env
RETURN_ENGINE_URL=http://localhost:8000/api/v1
RETURN_ENGINE_API_KEY=your-api-key-from-return-engine
```

### How It Works

1. When a customer requests a return, the e-commerce backend calls the Return Policy Engine
2. The engine evaluates the request based on:
   - Buyer history (return rate, account age, review score)
   - Product details (category, price, return rate)
   - Request context (days since order, return reason)
3. The engine returns:
   - Eligibility score (0-100)
   - Risk level (low/medium/high)
   - Recommendation (APPROVE/REVIEW/DENY)
   - Risk flags detected
4. Based on the recommendation, the return is auto-approved, auto-denied, or queued for manual review

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/addresses` - Get user addresses

### Products
- `GET /api/v1/products` - List products
- `GET /api/v1/products/featured` - Featured products
- `GET /api/v1/products/{id}` - Product details
- `POST /api/v1/products` - Create product (seller)

### Cart
- `GET /api/v1/cart` - Get cart
- `POST /api/v1/cart/items` - Add to cart
- `PUT /api/v1/cart/items/{id}` - Update quantity
- `DELETE /api/v1/cart/items/{id}` - Remove item

### Orders
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{id}` - Order details
- `POST /api/v1/orders/{id}/cancel` - Cancel order

### Returns
- `POST /api/v1/returns` - Create return request
- `GET /api/v1/returns` - List returns
- `GET /api/v1/returns/{id}` - Return details
- `POST /api/v1/returns/{id}/cancel` - Cancel return

### Reviews
- `POST /api/v1/reviews` - Create review
- `GET /api/v1/reviews/product/{id}` - Product reviews

## Project Structure

```
ecommerce/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Settings
│   │   ├── database.py     # Database setup
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                # Next.js pages
│   ├── components/         # React components
│   ├── lib/                # Utilities, API client, store
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

MIT
