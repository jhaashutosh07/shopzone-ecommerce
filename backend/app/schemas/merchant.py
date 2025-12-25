from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class MerchantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class MerchantCreate(MerchantBase):
    password: str = Field(..., min_length=8)


class MerchantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    default_return_window: Optional[int] = Field(None, ge=1, le=365)
    fraud_threshold: Optional[float] = Field(None, ge=0, le=100)
    auto_approve_threshold: Optional[float] = Field(None, ge=0, le=100)


class MerchantResponse(MerchantBase):
    id: str
    default_return_window: int
    fraud_threshold: float
    auto_approve_threshold: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MerchantLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    merchant_id: Optional[str] = None


class APIKeyResponse(BaseModel):
    api_key: str
    message: str = "Store this key securely. It won't be shown again."
