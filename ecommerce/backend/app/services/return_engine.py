import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import get_settings
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem

settings = get_settings()


class ReturnEngineClient:
    """Client for integrating with the Return Policy Engine API."""

    def __init__(self):
        self.base_url = settings.return_engine_url
        self.api_key = settings.return_engine_api_key

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_return_score(
        self,
        buyer: User,
        product: Product,
        order: Order,
        order_item: OrderItem,
        return_reason: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get return eligibility score from the Return Policy Engine.

        Returns scoring response with:
        - score: 0-100 eligibility score
        - risk_level: low, medium, high
        - recommendation: APPROVE, REVIEW, DENY
        - risk_flags: List of detected risk indicators
        - confidence: Model confidence
        """
        if not self.api_key:
            # Return Policy Engine not configured
            return None

        payload = {
            "buyer_id": buyer.id,
            "product_id": product.id,
            "order_id": order.id,
            "order_date": order.created_at.isoformat(),
            "order_amount": order_item.total_price,
            "return_reason": return_reason,
            "reason_details": None
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/score",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Return Engine error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"Return Engine connection error: {e}")
            return None

    async def sync_buyer(self, buyer: User) -> bool:
        """Sync buyer data to Return Policy Engine."""
        if not self.api_key:
            return False

        payload = {
            "buyers": [{
                "external_buyer_id": buyer.id,
                "total_orders": buyer.total_orders,
                "total_returns": buyer.total_returns,
                "total_reviews": buyer.total_reviews,
                "avg_review_score": buyer.avg_review_score,
                "total_spend": buyer.total_spend,
                "account_created_at": buyer.created_at.isoformat()
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/buyers/sync",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Buyer sync error: {e}")
            return False

    async def sync_product(self, product: Product) -> bool:
        """Sync product data to Return Policy Engine."""
        if not self.api_key:
            return False

        payload = {
            "products": [{
                "external_product_id": product.id,
                "name": product.name,
                "category": product.category.value,
                "price": product.price,
                "total_sold": product.total_sold,
                "total_returned": product.total_returned,
                "custom_return_window": product.return_window_days
            }]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/products/sync",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Product sync error: {e}")
            return False


# Singleton instance
return_engine_client = ReturnEngineClient()
