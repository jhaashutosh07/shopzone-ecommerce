from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import re

from app.database import get_db
from app.models.user import User
from app.models.product import Product, ProductImage, ProductCategory
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductImageCreate, ProductImageResponse
)
from app.services.auth import get_current_user, get_current_seller

router = APIRouter(prefix="/products", tags=["Products"])


def create_slug(name: str, db: Session) -> str:
    """Create a unique slug from product name."""
    base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    slug = base_slug
    counter = 1

    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


@router.get("", response_model=List[ProductListResponse])
def list_products(
    query: Optional[str] = None,
    category: Optional[ProductCategory] = None,
    subcategory: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock_only: bool = False,
    sort_by: str = "relevance",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List products with filtering and search."""
    q = db.query(Product).filter(Product.is_active == True)

    # Text search
    if query:
        search_term = f"%{query}%"
        q = q.filter(or_(
            Product.name.ilike(search_term),
            Product.description.ilike(search_term),
            Product.brand.ilike(search_term)
        ))

    # Category filter
    if category:
        q = q.filter(Product.category == category)

    if subcategory:
        q = q.filter(Product.subcategory == subcategory)

    if brand:
        q = q.filter(Product.brand == brand)

    # Price filter
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    # Stock filter
    if in_stock_only:
        q = q.filter(Product.stock_quantity > 0)

    # Sorting
    if sort_by == "price_low":
        q = q.order_by(Product.price.asc())
    elif sort_by == "price_high":
        q = q.order_by(Product.price.desc())
    elif sort_by == "newest":
        q = q.order_by(Product.created_at.desc())
    elif sort_by == "popular":
        q = q.order_by(Product.total_sold.desc())
    else:  # relevance (default) or rating
        q = q.order_by(Product.is_featured.desc(), Product.total_sold.desc())

    # Pagination
    total = q.count()
    products = q.offset((page - 1) * per_page).limit(per_page).all()

    # Filter by rating (post-query since it's computed)
    if min_rating is not None:
        products = [p for p in products if p.avg_rating >= min_rating]

    return [ProductListResponse(
        id=p.id,
        name=p.name,
        slug=p.slug,
        category=p.category,
        price=p.price,
        compare_at_price=p.compare_at_price,
        discount_percentage=p.discount_percentage,
        avg_rating=p.avg_rating,
        review_count=p.review_count,
        in_stock=p.in_stock,
        primary_image=p.primary_image,
        seller_id=p.seller_id
    ) for p in products]


@router.get("/featured", response_model=List[ProductListResponse])
def get_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured products for homepage."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.is_featured == True
    ).order_by(Product.total_sold.desc()).limit(limit).all()

    return [ProductListResponse(
        id=p.id,
        name=p.name,
        slug=p.slug,
        category=p.category,
        price=p.price,
        compare_at_price=p.compare_at_price,
        discount_percentage=p.discount_percentage,
        avg_rating=p.avg_rating,
        review_count=p.review_count,
        in_stock=p.in_stock,
        primary_image=p.primary_image,
        seller_id=p.seller_id
    ) for p in products]


@router.get("/deals", response_model=List[ProductListResponse])
def get_deals(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get products with discounts."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.compare_at_price != None,
        Product.compare_at_price > Product.price
    ).order_by((Product.compare_at_price - Product.price).desc()).limit(limit).all()

    return [ProductListResponse(
        id=p.id,
        name=p.name,
        slug=p.slug,
        category=p.category,
        price=p.price,
        compare_at_price=p.compare_at_price,
        discount_percentage=p.discount_percentage,
        avg_rating=p.avg_rating,
        review_count=p.review_count,
        in_stock=p.in_stock,
        primary_image=p.primary_image,
        seller_id=p.seller_id
    ) for p in products]


@router.get("/category/{category}", response_model=List[ProductListResponse])
def get_products_by_category(
    category: ProductCategory,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get products by category."""
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.category == category
    ).order_by(Product.total_sold.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return [ProductListResponse(
        id=p.id,
        name=p.name,
        slug=p.slug,
        category=p.category,
        price=p.price,
        compare_at_price=p.compare_at_price,
        discount_percentage=p.discount_percentage,
        avg_rating=p.avg_rating,
        review_count=p.review_count,
        in_stock=p.in_stock,
        primary_image=p.primary_image,
        seller_id=p.seller_id
    ) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get product details by ID or slug."""
    product = db.query(Product).filter(
        or_(Product.id == product_id, Product.slug == product_id)
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Increment view count
    product.view_count += 1
    db.commit()

    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        short_description=product.short_description,
        category=product.category,
        subcategory=product.subcategory,
        brand=product.brand,
        price=product.price,
        compare_at_price=product.compare_at_price,
        sku=product.sku,
        stock_quantity=product.stock_quantity,
        weight=product.weight,
        dimensions=product.dimensions,
        color=product.color,
        size=product.size,
        material=product.material,
        return_window_days=product.return_window_days,
        is_returnable=product.is_returnable,
        seller_id=product.seller_id,
        is_active=product.is_active,
        is_featured=product.is_featured,
        total_sold=product.total_sold,
        total_returned=product.total_returned,
        view_count=product.view_count,
        return_rate=product.return_rate,
        avg_rating=product.avg_rating,
        review_count=product.review_count,
        discount_percentage=product.discount_percentage,
        in_stock=product.in_stock,
        primary_image=product.primary_image,
        images=[ProductImageResponse(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            is_primary=img.is_primary,
            sort_order=img.sort_order
        ) for img in product.images],
        created_at=product.created_at
    )


# Seller endpoints
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Create a new product (seller only)."""
    # Check if SKU exists
    existing = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    # Create product
    product = Product(
        seller_id=seller.id,
        name=product_data.name,
        slug=create_slug(product_data.name, db),
        description=product_data.description,
        short_description=product_data.short_description,
        category=product_data.category,
        subcategory=product_data.subcategory,
        brand=product_data.brand,
        price=product_data.price,
        compare_at_price=product_data.compare_at_price,
        sku=product_data.sku,
        stock_quantity=product_data.stock_quantity,
        weight=product_data.weight,
        dimensions=product_data.dimensions,
        color=product_data.color,
        size=product_data.size,
        material=product_data.material,
        return_window_days=product_data.return_window_days,
        is_returnable=product_data.is_returnable
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Add images
    for img_data in product_data.images:
        image = ProductImage(
            product_id=product.id,
            url=img_data.url,
            alt_text=img_data.alt_text,
            is_primary=img_data.is_primary,
            sort_order=img_data.sort_order
        )
        db.add(image)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        short_description=product.short_description,
        category=product.category,
        subcategory=product.subcategory,
        brand=product.brand,
        price=product.price,
        compare_at_price=product.compare_at_price,
        sku=product.sku,
        stock_quantity=product.stock_quantity,
        weight=product.weight,
        dimensions=product.dimensions,
        color=product.color,
        size=product.size,
        material=product.material,
        return_window_days=product.return_window_days,
        is_returnable=product.is_returnable,
        seller_id=product.seller_id,
        is_active=product.is_active,
        is_featured=product.is_featured,
        total_sold=product.total_sold,
        total_returned=product.total_returned,
        view_count=product.view_count,
        return_rate=product.return_rate,
        avg_rating=product.avg_rating,
        review_count=product.review_count,
        discount_percentage=product.discount_percentage,
        in_stock=product.in_stock,
        primary_image=product.primary_image,
        images=[ProductImageResponse(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            is_primary=img.is_primary,
            sort_order=img.sort_order
        ) for img in product.images],
        created_at=product.created_at
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    update_data: ProductUpdate,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Update a product (seller only)."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == seller.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        short_description=product.short_description,
        category=product.category,
        subcategory=product.subcategory,
        brand=product.brand,
        price=product.price,
        compare_at_price=product.compare_at_price,
        sku=product.sku,
        stock_quantity=product.stock_quantity,
        weight=product.weight,
        dimensions=product.dimensions,
        color=product.color,
        size=product.size,
        material=product.material,
        return_window_days=product.return_window_days,
        is_returnable=product.is_returnable,
        seller_id=product.seller_id,
        is_active=product.is_active,
        is_featured=product.is_featured,
        total_sold=product.total_sold,
        total_returned=product.total_returned,
        view_count=product.view_count,
        return_rate=product.return_rate,
        avg_rating=product.avg_rating,
        review_count=product.review_count,
        discount_percentage=product.discount_percentage,
        in_stock=product.in_stock,
        primary_image=product.primary_image,
        images=[ProductImageResponse(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            is_primary=img.is_primary,
            sort_order=img.sort_order
        ) for img in product.images],
        created_at=product.created_at
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Delete a product (seller only)."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == seller.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()


@router.get("/seller/my-products", response_model=List[ProductResponse])
def get_my_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """Get seller's own products."""
    products = db.query(Product).filter(
        Product.seller_id == seller.id
    ).order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return [ProductResponse(
        id=p.id,
        name=p.name,
        slug=p.slug,
        description=p.description,
        short_description=p.short_description,
        category=p.category,
        subcategory=p.subcategory,
        brand=p.brand,
        price=p.price,
        compare_at_price=p.compare_at_price,
        sku=p.sku,
        stock_quantity=p.stock_quantity,
        weight=p.weight,
        dimensions=p.dimensions,
        color=p.color,
        size=p.size,
        material=p.material,
        return_window_days=p.return_window_days,
        is_returnable=p.is_returnable,
        seller_id=p.seller_id,
        is_active=p.is_active,
        is_featured=p.is_featured,
        total_sold=p.total_sold,
        total_returned=p.total_returned,
        view_count=p.view_count,
        return_rate=p.return_rate,
        avg_rating=p.avg_rating,
        review_count=p.review_count,
        discount_percentage=p.discount_percentage,
        in_stock=p.in_stock,
        primary_image=p.primary_image,
        images=[ProductImageResponse(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            is_primary=img.is_primary,
            sort_order=img.sort_order
        ) for img in p.images],
        created_at=p.created_at
    ) for p in products]
