"""Database seeding for demos and development.

Creates the catalog plus two demo buyer personas designed to showcase the
Return Policy Engine end to end:

- demo.trusted@shopzone.com  - long history, almost no returns
    -> return requests get auto-APPROVED
- demo.risky@shopzone.com    - brand-new account, 5 returns in 8 orders
    -> return requests get flagged or auto-DENIED

Both have delivered orders ready to be returned. Password: demo1234
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.product import Product, ProductImage, ProductCategory
from app.models.cart import Cart
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.review import Review
from app.services.auth import get_password_hash

DEMO_PASSWORD = "demo1234"

PRODUCTS_DATA = [
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

_order_counter = 0


def _make_delivered_order(
    db: Session,
    user: User,
    products_with_qty: list,
    ordered_days_ago: int,
    delivered_days_ago: int,
) -> Order:
    """Create a delivered, paid order so its items are returnable."""
    global _order_counter
    _order_counter += 1

    now = datetime.utcnow()
    subtotal = sum(p.price * qty for p, qty in products_with_qty)
    tax = round(subtotal * 0.18, 2)
    shipping_fee = 0.0 if subtotal > 500 else 40.0
    total = round(subtotal + tax + shipping_fee, 2)

    order = Order(
        user_id=user.id,
        order_number=f"ORD-{now.strftime('%Y%m')}-{_order_counter:05d}",
        status=OrderStatus.DELIVERED,
        payment_status=PaymentStatus.PAID,
        subtotal=subtotal,
        tax=tax,
        shipping_fee=shipping_fee,
        discount=0.0,
        total=total,
        payment_method="upi",
        payment_id=f"pay_demo_{_order_counter:05d}",
        shipping_name=user.full_name,
        shipping_phone="9876543210",
        shipping_address="42 MG Road",
        shipping_city="Bengaluru",
        shipping_state="Karnataka",
        shipping_postal_code="560001",
        shipping_country="India",
        created_at=now - timedelta(days=ordered_days_ago),
        confirmed_at=now - timedelta(days=ordered_days_ago),
        shipped_at=now - timedelta(days=ordered_days_ago - 1),
        delivered_at=now - timedelta(days=delivered_days_ago),
    )
    db.add(order)
    db.flush()

    for product, qty in products_with_qty:
        image = product.images[0].url if product.images else None
        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_image=image,
            product_sku=product.sku,
            unit_price=product.price,
            quantity=qty,
            total_price=product.price * qty,
            return_window_days=30,
            created_at=order.created_at,
        ))
    return order


def seed_database(db: Session) -> dict:
    """Idempotent seed: catalog, staff accounts, and demo buyer personas."""
    if db.query(User).first():
        return {"message": "Database already seeded"}

    now = datetime.utcnow()

    admin = User(
        email="admin@shopzone.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_verified=True
    )
    db.add(admin)

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

    buyer = User(
        email="buyer@example.com",
        hashed_password=get_password_hash("buyer123"),
        full_name="John Doe",
        role=UserRole.BUYER,
        total_orders=5,
        total_spend=2500.00
    )
    db.add(buyer)

    # Demo persona 1: loyal customer -> engine should auto-approve returns
    trusted = User(
        email="demo.trusted@shopzone.com",
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name="Trusted Tina",
        role=UserRole.BUYER,
        is_verified=True,
        total_orders=48,
        total_returns=1,
        total_reviews=32,
        total_spend=210000.00,
        created_at=now - timedelta(days=500),
    )
    db.add(trusted)

    # Demo persona 2: serial returner on a new account -> engine should flag/deny
    risky = User(
        email="demo.risky@shopzone.com",
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name="Risky Rahul",
        role=UserRole.BUYER,
        is_verified=True,
        total_orders=8,
        total_returns=5,
        total_reviews=0,
        total_spend=32000.00,
        created_at=now - timedelta(days=12),
    )
    db.add(risky)

    db.commit()
    for user in (seller, buyer, trusted, risky):
        db.refresh(user)

    for user in (buyer, trusted, risky):
        db.add(Cart(user_id=user.id))

    products_by_name = {}
    for idx, prod_data in enumerate(PRODUCTS_DATA):
        data = dict(prod_data)
        images = data.pop("images", [])

        product = Product(
            seller_id=seller.id,
            slug=data["name"].lower().replace(" ", "-").replace(",", ""),
            sku=f"SKU-{idx + 1:04d}",
            **data
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        products_by_name[product.name] = product

        for img_idx, img_url in enumerate(images):
            db.add(ProductImage(
                product_id=product.id,
                url=img_url,
                alt_text=data["name"],
                is_primary=(img_idx == 0),
                sort_order=img_idx
            ))
    db.commit()

    # Delivered orders so both personas can immediately request returns
    _make_delivered_order(
        db, trusted,
        [(products_by_name["Classic Blue Denim Jeans"], 1),
         (products_by_name["Casual Cotton T-Shirt"], 2)],
        ordered_days_ago=8, delivered_days_ago=4,
    )
    _make_delivered_order(
        db, trusted,
        [(products_by_name["Wireless Bluetooth Headphones"], 1)],
        ordered_days_ago=10, delivered_days_ago=5,
    )
    _make_delivered_order(
        db, risky,
        [(products_by_name["Smart Fitness Watch"], 1)],
        ordered_days_ago=9, delivered_days_ago=6,
    )
    _make_delivered_order(
        db, risky,
        [(products_by_name["Wireless Bluetooth Headphones"], 1),
         (products_by_name["Running Shoes Pro"], 1)],
        ordered_days_ago=11, delivered_days_ago=8,
    )
    db.commit()

    # Reviews so the trusted persona's avg_review_score reflects a real
    # engaged customer (the property averages actual review rows)
    for i, (product_name, rating) in enumerate([
        ("Classic Blue Denim Jeans", 5),
        ("Casual Cotton T-Shirt", 5),
        ("Wireless Bluetooth Headphones", 4),
        ("Running Shoes Pro", 5),
        ("Yoga Mat Premium", 5),
    ]):
        db.add(Review(
            user_id=trusted.id,
            product_id=products_by_name[product_name].id,
            rating=rating,
            title="Great product",
            content="Exactly as described, would buy again.",
            is_verified_purchase=True,
            created_at=now - timedelta(days=30 * (i + 1)),
        ))
    db.commit()

    return {
        "message": "Database seeded successfully",
        "data": {
            "users": 5,
            "products": len(PRODUCTS_DATA),
            "demo_accounts": {
                "trusted_buyer": "demo.trusted@shopzone.com / demo1234",
                "risky_buyer": "demo.risky@shopzone.com / demo1234",
            }
        }
    }
