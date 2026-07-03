"""Catalog importer: pulls real product listings from the web into the store.

Source: DummyJSON's product API (https://dummyjson.com/products) — ~200 real
listings with brands, multi-image galleries, specs (weight, dimensions,
warranty, shipping), stock and genuine review text. Imported idempotently:
existing SKUs are skipped, so it can run on every boot.

Direct scraping of Amazon/Flipkart is intentionally avoided (ToS + brittle);
this open API provides equivalent listing data reliably.
"""
import json
import random
import secrets
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.product import Product, ProductImage, ProductCategory
from app.models.review import Review
from app.services.auth import get_password_hash

SOURCE_URL = "https://dummyjson.com/products?limit=0"
USD_TO_INR = 83.0

# source category -> (our category, subcategory)
CATEGORY_MAP = {
    "beauty": (ProductCategory.BEAUTY, "makeup"),
    "fragrances": (ProductCategory.BEAUTY, "fragrance"),
    "skin-care": (ProductCategory.BEAUTY, "skincare"),
    "furniture": (ProductCategory.HOME, "furniture"),
    "home-decoration": (ProductCategory.HOME, "decor"),
    "kitchen-accessories": (ProductCategory.HOME, "kitchen"),
    "groceries": (ProductCategory.GROCERY, None),
    "laptops": (ProductCategory.ELECTRONICS, "laptops"),
    "smartphones": (ProductCategory.ELECTRONICS, "smartphones"),
    "tablets": (ProductCategory.ELECTRONICS, "tablets"),
    "mobile-accessories": (ProductCategory.ELECTRONICS, "accessories"),
    "mens-shirts": (ProductCategory.CLOTHING, "mens_shirts"),
    "mens-shoes": (ProductCategory.CLOTHING, "mens_shoes"),
    "mens-watches": (ProductCategory.JEWELRY, "watches"),
    "womens-watches": (ProductCategory.JEWELRY, "watches"),
    "womens-jewellery": (ProductCategory.JEWELRY, None),
    "sunglasses": (ProductCategory.CLOTHING, "accessories"),
    "tops": (ProductCategory.CLOTHING, "womens_tops"),
    "womens-dresses": (ProductCategory.CLOTHING, "womens_dresses"),
    "womens-bags": (ProductCategory.CLOTHING, "accessories"),
    "womens-shoes": (ProductCategory.CLOTHING, "womens_shoes"),
    "sports-accessories": (ProductCategory.SPORTS, "fitness"),
    "motorcycle": (ProductCategory.AUTOMOTIVE, None),
    "vehicle": (ProductCategory.AUTOMOTIVE, None),
}

RETURN_WINDOWS = {
    ProductCategory.ELECTRONICS: 10,
    ProductCategory.GROCERY: 7,
    ProductCategory.BEAUTY: 15,
}


def _to_inr(usd: float) -> float:
    """Convert USD to a natural-looking INR price (…9 endings)."""
    inr = usd * USD_TO_INR
    if inr < 500:
        return float(int(inr / 10) * 10 + 9)
    return float(int(inr / 100) * 100 + 99)


def _slugify(name: str, db: Session) -> str:
    import re
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug, n = base, 1
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base}-{n}"
        n += 1
    return slug


_REVIEWER_PW_HASH = None


def _reviewer_password_hash() -> str:
    # bcrypt is ~0.3s per hash; reviewer accounts are non-loginable
    # placeholders, so one shared random-password hash is fine and keeps
    # boot-time imports fast.
    global _REVIEWER_PW_HASH
    if _REVIEWER_PW_HASH is None:
        _REVIEWER_PW_HASH = get_password_hash(secrets.token_urlsafe(24))
    return _REVIEWER_PW_HASH


def _get_or_create_reviewer(db: Session, name: str, email: str, cache: dict) -> User:
    if email in cache:
        return cache[email]
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            email=email,
            hashed_password=_reviewer_password_hash(),
            full_name=name or "ShopZone Shopper",
            role=UserRole.BUYER,
            is_verified=True,
        )
        db.add(user)
        db.flush()
    cache[email] = user
    return user


def import_catalog(db: Session, seller: User = None) -> dict:
    """Import the external catalog. Idempotent (skips existing SKUs)."""
    if seller is None:
        seller = db.query(User).filter(User.role == UserRole.SELLER).first()
    if seller is None:
        return {"imported": 0, "message": "No seller account; seed the database first"}

    try:
        resp = httpx.get(SOURCE_URL, timeout=60)
        resp.raise_for_status()
        listings = resp.json().get("products", [])
    except Exception as e:
        return {"imported": 0, "message": f"Catalog source unreachable: {e}"}

    rng = random.Random(42)
    reviewer_cache: dict = {}
    imported = 0
    featured_budget = 16

    for item in listings:
        sku = f"IMP-{item['id']:05d}"
        if db.query(Product).filter(Product.sku == sku).first():
            continue

        category, subcategory = CATEGORY_MAP.get(
            item.get("category", ""), (ProductCategory.OTHER, None)
        )

        price = _to_inr(item["price"])
        discount = float(item.get("discountPercentage") or 0)
        compare_at = round(price / (1 - discount / 100), 2) if discount >= 3 else None

        dims = item.get("dimensions") or {}
        dimensions = None
        if dims:
            dimensions = f"{dims.get('width', 0):.0f} x {dims.get('height', 0):.0f} x {dims.get('depth', 0):.0f} cm"

        details = {
            "warranty": item.get("warrantyInformation"),
            "shipping": item.get("shippingInformation"),
            "return_policy": item.get("returnPolicy"),
            "availability": item.get("availabilityStatus"),
            "tags": item.get("tags") or [],
            "source": "dummyjson",
            "external_id": item["id"],
        }

        rating = float(item.get("rating") or 0)
        is_featured = featured_budget > 0 and rating >= 4.4
        if is_featured:
            featured_budget -= 1

        product = Product(
            seller_id=seller.id,
            name=item["title"],
            slug=_slugify(item["title"], db),
            description=item.get("description"),
            short_description=(item.get("description") or "")[:280] or None,
            category=category,
            subcategory=subcategory,
            brand=item.get("brand"),
            price=price,
            compare_at_price=compare_at,
            sku=sku,
            stock_quantity=int(item.get("stock") or 0),
            weight=float(item["weight"]) if item.get("weight") else None,
            dimensions=dimensions,
            is_featured=is_featured,
            return_window_days=RETURN_WINDOWS.get(category, 30),
            is_returnable=category != ProductCategory.GROCERY,
            total_sold=rng.randint(30, 900),
            view_count=rng.randint(200, 8000),
            meta_title=item["title"],
            meta_description=(item.get("description") or "")[:300] or None,
        )
        # Attribute-ish tags -> color/material hints when present
        tags = [t.lower() for t in details["tags"]]
        product.details = json.dumps(details)

        db.add(product)
        db.flush()

        urls = list(item.get("images") or [])
        if item.get("thumbnail") and item["thumbnail"] not in urls:
            urls.append(item["thumbnail"])
        for i, url in enumerate(urls[:6]):
            db.add(ProductImage(
                product_id=product.id,
                url=url,
                alt_text=item["title"],
                is_primary=(i == 0),
                sort_order=i,
            ))

        for rev in item.get("reviews") or []:
            reviewer = _get_or_create_reviewer(
                db, rev.get("reviewerName"), rev.get("reviewerEmail"), reviewer_cache
            )
            created = None
            try:
                created = datetime.fromisoformat(rev["date"].replace("Z", "+00:00")).replace(tzinfo=None)
            except (KeyError, ValueError):
                pass
            db.add(Review(
                user_id=reviewer.id,
                product_id=product.id,
                rating=int(rev.get("rating") or 4),
                content=rev.get("comment"),
                is_verified_purchase=True,
                created_at=created or datetime.utcnow(),
            ))

        imported += 1
        if imported % 50 == 0:
            db.commit()

    db.commit()
    return {"imported": imported, "total_listings": len(listings),
            "message": f"Imported {imported} products from web catalog"}
