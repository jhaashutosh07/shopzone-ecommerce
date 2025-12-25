from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.cart import Cart
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, UserUpdate, Token,
    AddressCreate, AddressUpdate, AddressResponse
)
from app.services.auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, get_current_active_user
)
from app.models.address import Address
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (buyer or seller)."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create cart for buyer
    if user.role == UserRole.BUYER:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()

    # Generate token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            avatar_url=user.avatar_url,
            store_name=user.store_name,
            total_orders=user.total_orders,
            total_returns=user.total_returns,
            total_spend=user.total_spend,
            return_rate=user.return_rate,
            account_age_days=user.account_age_days,
            created_at=user.created_at
        )
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            avatar_url=user.avatar_url,
            store_name=user.store_name,
            total_orders=user.total_orders,
            total_returns=user.total_returns,
            total_spend=user.total_spend,
            return_rate=user.return_rate,
            account_age_days=user.account_age_days,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
        store_name=current_user.store_name,
        total_orders=current_user.total_orders,
        total_returns=current_user.total_returns,
        total_spend=current_user.total_spend,
        return_rate=current_user.return_rate,
        account_age_days=current_user.account_age_days,
        created_at=current_user.created_at
    )


@router.put("/me", response_model=UserResponse)
def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
        store_name=current_user.store_name,
        total_orders=current_user.total_orders,
        total_returns=current_user.total_returns,
        total_spend=current_user.total_spend,
        return_rate=current_user.return_rate,
        account_age_days=current_user.account_age_days,
        created_at=current_user.created_at
    )


# Address endpoints
@router.get("/addresses", response_model=list[AddressResponse])
def get_addresses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all addresses for current user."""
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return [AddressResponse(
        id=addr.id,
        user_id=addr.user_id,
        full_name=addr.full_name,
        phone=addr.phone,
        address_line1=addr.address_line1,
        address_line2=addr.address_line2,
        city=addr.city,
        state=addr.state,
        postal_code=addr.postal_code,
        country=addr.country,
        address_type=addr.address_type,
        is_default=addr.is_default,
        full_address=addr.full_address,
        created_at=addr.created_at
    ) for addr in addresses]


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new address."""
    # If this is default, unset other defaults
    if address_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})

    address = Address(
        user_id=current_user.id,
        **address_data.model_dump()
    )
    db.add(address)
    db.commit()
    db.refresh(address)

    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        full_name=address.full_name,
        phone=address.phone,
        address_line1=address.address_line1,
        address_line2=address.address_line2,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        address_type=address.address_type,
        is_default=address.is_default,
        full_address=address.full_address,
        created_at=address.created_at
    )


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: str,
    update_data: AddressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an address."""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # If setting as default, unset other defaults
    if update_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True,
            Address.id != address_id
        ).update({"is_default": False})

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        full_name=address.full_name,
        phone=address.phone,
        address_line1=address.address_line1,
        address_line2=address.address_line2,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        address_type=address.address_type,
        is_default=address.is_default,
        full_address=address.full_address,
        created_at=address.created_at
    )


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an address."""
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
