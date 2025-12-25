from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, products, cart, orders, returns, reviews, wishlist

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Full-featured E-commerce API with Return Policy Engine integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.api_prefix
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Seed data endpoint for development
@app.post("/api/v1/seed")
def seed_database():
    """Seed database with sample data for development."""
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.models.user import User, UserRole
    from app.models.product import Product, ProductImage, ProductCategory
    from app.models.cart import Cart
    from app.services.auth import get_password_hash
    import random

    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            return {"message": "Database already seeded"}

        # Create admin user
        admin = User(
            email="admin@shopzone.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_verified=True
        )
        db.add(admin)

        # Create seller
        seller = User(
            email="seller@shopzone.com",
            hashed_password=get_password_hash("seller123"),
            full_name="Fashion Store",
            role=UserRole.SELLER,
            is_verified=True,
            store_name="Fashion Store",
            store_description="Premium fashion and clothing"
        )
        db.add(seller)

        # Create buyer
        buyer = User(
            email="buyer@example.com",
            hashed_password=get_password_hash("buyer123"),
            full_name="John Doe",
            role=UserRole.BUYER,
            total_orders=5,
            total_spend=2500.00
        )
        db.add(buyer)

        db.commit()
        db.refresh(seller)
        db.refresh(buyer)

        # Create cart for buyer
        cart = Cart(user_id=buyer.id)
        db.add(cart)

        # Sample products
        products_data = [
            {
                "name": "Classic Blue Denim Jeans",
                "category": ProductCategory.CLOTHING,
                "subcategory": "mens_pants",
                "price": 1999.00,
                "compare_at_price": 2999.00,
                "description": "Premium quality denim jeans with a classic fit. Perfect for casual and semi-formal occasions.",
                "brand": "LeviStyle",
                "stock_quantity": 100,
                "color": "Blue",
                "size": "M, L, XL, XXL",
                "material": "100% Cotton Denim",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500",
                    "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500"
                ]
            },
            {
                "name": "Slim Fit Chino Pants",
                "category": ProductCategory.CLOTHING,
                "subcategory": "mens_pants",
                "price": 1499.00,
                "compare_at_price": 1999.00,
                "description": "Comfortable slim fit chinos perfect for office and casual wear.",
                "brand": "UrbanWear",
                "stock_quantity": 75,
                "color": "Khaki",
                "size": "30, 32, 34, 36",
                "material": "Cotton Blend",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=500"
                ]
            },
            {
                "name": "Wireless Bluetooth Headphones",
                "category": ProductCategory.ELECTRONICS,
                "subcategory": "headphones",
                "price": 4999.00,
                "compare_at_price": 6999.00,
                "description": "Premium wireless headphones with active noise cancellation and 30-hour battery life.",
                "brand": "SoundMax",
                "stock_quantity": 50,
                "color": "Black",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
                ]
            },
            {
                "name": "Smart Fitness Watch",
                "category": ProductCategory.ELECTRONICS,
                "subcategory": "smart_home",
                "price": 7999.00,
                "compare_at_price": 9999.00,
                "description": "Track your fitness goals with heart rate monitoring, GPS, and 7-day battery life.",
                "brand": "FitTech",
                "stock_quantity": 30,
                "color": "Silver",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
                ]
            },
            {
                "name": "Casual Cotton T-Shirt",
                "category": ProductCategory.CLOTHING,
                "subcategory": "mens_shirts",
                "price": 599.00,
                "compare_at_price": 899.00,
                "description": "Soft, breathable cotton t-shirt for everyday comfort.",
                "brand": "BasicWear",
                "stock_quantity": 200,
                "color": "White, Black, Navy",
                "size": "S, M, L, XL",
                "material": "100% Cotton",
                "images": [
                    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"
                ]
            },
            {
                "name": "Running Shoes Pro",
                "category": ProductCategory.SPORTS,
                "subcategory": "fitness",
                "price": 3999.00,
                "compare_at_price": 5499.00,
                "description": "Lightweight running shoes with superior cushioning and support.",
                "brand": "SpeedRun",
                "stock_quantity": 60,
                "color": "Red/Black",
                "size": "7, 8, 9, 10, 11",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"
                ]
            },
            {
                "name": "Elegant Summer Dress",
                "category": ProductCategory.CLOTHING,
                "subcategory": "womens_dresses",
                "price": 2499.00,
                "compare_at_price": 3499.00,
                "description": "Beautiful floral print summer dress, perfect for any occasion.",
                "brand": "FloraStyle",
                "stock_quantity": 45,
                "color": "Floral Blue",
                "size": "XS, S, M, L",
                "material": "Polyester Blend",
                "is_featured": True,
                "images": [
                    "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500"
                ]
            },
            {
                "name": "Leather Wallet",
                "category": ProductCategory.CLOTHING,
                "subcategory": "accessories",
                "price": 1299.00,
                "compare_at_price": 1799.00,
                "description": "Genuine leather wallet with multiple card slots and coin pocket.",
                "brand": "LeatherCraft",
                "stock_quantity": 80,
                "color": "Brown",
                "material": "Genuine Leather",
                "images": [
                    "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500"
                ]
            },
            {
                "name": "Smartphone Stand",
                "category": ProductCategory.ELECTRONICS,
                "subcategory": "accessories",
                "price": 499.00,
                "description": "Adjustable aluminum smartphone stand for desk use.",
                "brand": "TechGear",
                "stock_quantity": 150,
                "color": "Silver",
                "images": [
                    "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"
                ]
            },
            {
                "name": "Yoga Mat Premium",
                "category": ProductCategory.SPORTS,
                "subcategory": "fitness",
                "price": 1499.00,
                "compare_at_price": 1999.00,
                "description": "Extra thick yoga mat with non-slip surface and carrying strap.",
                "brand": "YogaLife",
                "stock_quantity": 70,
                "color": "Purple",
                "images": [
                    "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500"
                ]
            }
        ]

        for idx, prod_data in enumerate(products_data):
            images = prod_data.pop("images", [])

            product = Product(
                seller_id=seller.id,
                slug=prod_data["name"].lower().replace(" ", "-").replace(",", ""),
                sku=f"SKU-{idx+1:04d}",
                **prod_data
            )
            db.add(product)
            db.commit()
            db.refresh(product)

            # Add images
            for img_idx, img_url in enumerate(images):
                image = ProductImage(
                    product_id=product.id,
                    url=img_url,
                    alt_text=prod_data["name"],
                    is_primary=(img_idx == 0),
                    sort_order=img_idx
                )
                db.add(image)

        db.commit()

        return {
            "message": "Database seeded successfully",
            "data": {
                "users": 3,
                "products": len(products_data)
            }
        }

    finally:
        db.close()
