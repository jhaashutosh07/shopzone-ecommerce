from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.BUYER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    store_name: Optional[str] = None
    store_description: Optional[str] = None


class UserResponse(UserBase):
    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    store_name: Optional[str] = None
    total_orders: int
    total_returns: int
    total_spend: float
    return_rate: float
    account_age_days: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    id: str
    full_name: str
    avatar_url: Optional[str] = None
    store_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None


class AddressCreate(BaseModel):
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    address_type: str = "home"
    is_default: bool = False


class AddressUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    address_type: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(AddressCreate):
    id: str
    user_id: str
    full_address: str
    created_at: datetime

    class Config:
        from_attributes = True
