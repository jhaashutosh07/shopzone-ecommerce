from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.merchant import Merchant
from app.schemas.merchant import (
    MerchantCreate,
    MerchantResponse,
    MerchantUpdate,
    Token,
    APIKeyResponse,
)
from app.services.auth import AuthService, get_current_merchant

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
def register_merchant(
    merchant_data: MerchantCreate,
    db: Session = Depends(get_db)
):
    """Register a new merchant account."""
    # Check if email already exists
    existing = db.query(Merchant).filter(Merchant.email == merchant_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create merchant
    merchant = Merchant(
        name=merchant_data.name,
        email=merchant_data.email,
        password_hash=AuthService.hash_password(merchant_data.password),
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)

    return merchant


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to get access token."""
    merchant = AuthService.authenticate_merchant(db, form_data.username, form_data.password)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(data={"sub": merchant.id})
    return Token(access_token=access_token)


@router.get("/me", response_model=MerchantResponse)
def get_current_merchant_info(
    merchant: Merchant = Depends(get_current_merchant)
):
    """Get current merchant information."""
    return merchant


@router.put("/me", response_model=MerchantResponse)
def update_merchant(
    update_data: MerchantUpdate,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Update merchant settings."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(merchant, key, value)

    db.commit()
    db.refresh(merchant)
    return merchant


@router.post("/api-key", response_model=APIKeyResponse)
def generate_api_key(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Generate a new API key for the merchant."""
    # Generate new API key
    api_key = AuthService.generate_api_key()

    # Hash and store
    merchant.api_key_hash = AuthService.hash_api_key(api_key)
    db.commit()

    return APIKeyResponse(api_key=api_key)


@router.delete("/api-key", status_code=status.HTTP_204_NO_CONTENT)
def revoke_api_key(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db)
):
    """Revoke the current API key."""
    merchant.api_key_hash = None
    db.commit()
