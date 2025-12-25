from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader

from app.config import get_settings
from app.database import get_db
from app.models.merchant import Merchant

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key using SHA-256."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key."""
        return f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify a JWT token and return the merchant_id."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            merchant_id: str = payload.get("sub")
            if merchant_id is None:
                return None
            return merchant_id
        except JWTError:
            return None

    @staticmethod
    def authenticate_merchant(db: Session, email: str, password: str) -> Optional[Merchant]:
        """Authenticate a merchant by email and password."""
        merchant = db.query(Merchant).filter(Merchant.email == email).first()
        if not merchant:
            return None
        if not AuthService.verify_password(password, merchant.password_hash):
            return None
        return merchant

    @staticmethod
    def get_merchant_by_api_key(db: Session, api_key: str) -> Optional[Merchant]:
        """Get a merchant by API key."""
        api_key_hash = AuthService.hash_api_key(api_key)
        return db.query(Merchant).filter(
            Merchant.api_key_hash == api_key_hash,
            Merchant.is_active == True
        ).first()


async def get_current_merchant(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Merchant:
    """Dependency to get the current authenticated merchant from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    merchant_id = AuthService.verify_token(token)
    if merchant_id is None:
        raise credentials_exception
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if merchant is None:
        raise credentials_exception
    if not merchant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant account is disabled"
        )
    return merchant


async def get_merchant_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Merchant:
    """Dependency to get merchant from API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"X-API-Key": "Required"},
        )
    merchant = AuthService.get_merchant_by_api_key(db, api_key)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return merchant
