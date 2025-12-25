"""
E-commerce Training Data Generator
Generates realistic training data based on Flipkart and Amazon return patterns.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

# Category definitions with return rate characteristics
FLIPKART_CATEGORIES = {
    "fashion_clothing": {
        "return_rate": 0.25,  # High return rate - size/fit issues
        "fraud_rate": 0.08,
        "avg_price": 800,
        "price_range": (200, 5000),
        "common_reasons": ["size_issue", "not_as_described", "changed_mind"],
    },
    "fashion_footwear": {
        "return_rate": 0.22,
        "fraud_rate": 0.06,
        "avg_price": 1200,
        "price_range": (300, 8000),
        "common_reasons": ["size_issue", "defective", "not_as_described"],
    },
    "electronics_mobile": {
        "return_rate": 0.08,
        "fraud_rate": 0.12,  # Higher fraud attempts on expensive items
        "avg_price": 15000,
        "price_range": (5000, 80000),
        "common_reasons": ["defective", "not_as_described", "changed_mind"],
    },
    "electronics_accessories": {
        "return_rate": 0.12,
        "fraud_rate": 0.10,
        "avg_price": 500,
        "price_range": (100, 3000),
        "common_reasons": ["defective", "not_as_described", "wrong_item"],
    },
    "home_appliances": {
        "return_rate": 0.10,
        "fraud_rate": 0.05,
        "avg_price": 8000,
        "price_range": (1000, 50000),
        "common_reasons": ["defective", "damaged_in_shipping", "not_as_described"],
    },
    "beauty_personal_care": {
        "return_rate": 0.15,
        "fraud_rate": 0.07,
        "avg_price": 400,
        "price_range": (100, 2000),
        "common_reasons": ["not_as_described", "defective", "changed_mind"],
    },
    "books": {
        "return_rate": 0.03,
        "fraud_rate": 0.02,
        "avg_price": 300,
        "price_range": (100, 1500),
        "common_reasons": ["damaged_in_shipping", "wrong_item", "defective"],
    },
    "grocery": {
        "return_rate": 0.02,
        "fraud_rate": 0.01,
        "avg_price": 500,
        "price_range": (100, 2000),
        "common_reasons": ["defective", "arrived_late", "wrong_item"],
    },
}

AMAZON_CATEGORIES = {
    "clothing_apparel": {
        "return_rate": 0.30,  # Very high return rate
        "fraud_rate": 0.10,
        "avg_price": 1500,
        "price_range": (500, 10000),
        "common_reasons": ["size_issue", "not_as_described", "changed_mind"],
    },
    "shoes": {
        "return_rate": 0.28,
        "fraud_rate": 0.08,
        "avg_price": 2000,
        "price_range": (500, 15000),
        "common_reasons": ["size_issue", "not_as_described", "defective"],
    },
    "electronics": {
        "return_rate": 0.10,
        "fraud_rate": 0.15,
        "avg_price": 25000,
        "price_range": (1000, 150000),
        "common_reasons": ["defective", "not_as_described", "changed_mind"],
    },
    "computers": {
        "return_rate": 0.08,
        "fraud_rate": 0.12,
        "avg_price": 45000,
        "price_range": (15000, 200000),
        "common_reasons": ["defective", "not_as_described", "changed_mind"],
    },
    "home_kitchen": {
        "return_rate": 0.12,
        "fraud_rate": 0.06,
        "avg_price": 2000,
        "price_range": (200, 20000),
        "common_reasons": ["defective", "damaged_in_shipping", "not_as_described"],
    },
    "sports_fitness": {
        "return_rate": 0.14,
        "fraud_rate": 0.05,
        "avg_price": 1500,
        "price_range": (300, 15000),
        "common_reasons": ["size_issue", "not_as_described", "defective"],
    },
    "toys_games": {
        "return_rate": 0.08,
        "fraud_rate": 0.04,
        "avg_price": 800,
        "price_range": (200, 5000),
        "common_reasons": ["defective", "not_as_described", "damaged_in_shipping"],
    },
    "jewelry_watches": {
        "return_rate": 0.18,
        "fraud_rate": 0.20,  # High fraud on jewelry
        "avg_price": 5000,
        "price_range": (500, 100000),
        "common_reasons": ["not_as_described", "changed_mind", "defective"],
    },
}

# Buyer behavior profiles
BUYER_PROFILES = {
    "loyal_customer": {
        "weight": 0.30,
        "order_range": (20, 100),
        "return_rate_range": (0.02, 0.08),
        "review_score_range": (4.0, 5.0),
        "account_age_range": (365, 2000),
        "fraud_likelihood": 0.01,
    },
    "regular_customer": {
        "weight": 0.35,
        "order_range": (5, 30),
        "return_rate_range": (0.05, 0.15),
        "review_score_range": (3.5, 4.5),
        "account_age_range": (90, 730),
        "fraud_likelihood": 0.05,
    },
    "new_customer": {
        "weight": 0.20,
        "order_range": (1, 5),
        "return_rate_range": (0.10, 0.25),
        "review_score_range": (3.0, 5.0),
        "account_age_range": (1, 90),
        "fraud_likelihood": 0.15,
    },
    "high_returner": {
        "weight": 0.10,
        "order_range": (10, 50),
        "return_rate_range": (0.25, 0.50),
        "review_score_range": (2.0, 3.5),
        "account_age_range": (30, 365),
        "fraud_likelihood": 0.25,
    },
    "potential_fraudster": {
        "weight": 0.05,
        "order_range": (1, 10),
        "return_rate_range": (0.40, 0.80),
        "review_score_range": (1.0, 2.5),
        "account_age_range": (1, 60),
        "fraud_likelihood": 0.60,
    },
}

# Seasonal patterns (month -> multiplier for returns)
SEASONAL_PATTERNS = {
    1: 1.3,   # January - post holiday returns
    2: 1.0,
    3: 0.9,
    4: 0.9,
    5: 0.9,
    6: 1.0,
    7: 1.1,   # Summer sales
    8: 1.0,
    9: 0.9,
    10: 1.2,  # Festival season (Diwali)
    11: 1.4,  # Black Friday, festival returns
    12: 1.1,  # Holiday shopping
}


def generate_buyer_profile() -> Dict:
    """Generate a random buyer based on profiles."""
    profiles = list(BUYER_PROFILES.keys())
    weights = [BUYER_PROFILES[p]["weight"] for p in profiles]
    selected_profile = random.choices(profiles, weights=weights)[0]
    profile = BUYER_PROFILES[selected_profile]

    total_orders = random.randint(*profile["order_range"])
    return_rate = random.uniform(*profile["return_rate_range"])
    total_returns = int(total_orders * return_rate)

    return {
        "profile_type": selected_profile,
        "total_orders": total_orders,
        "total_returns": total_returns,
        "return_rate": return_rate,
        "avg_review_score": random.uniform(*profile["review_score_range"]),
        "account_age_days": random.randint(*profile["account_age_range"]),
        "total_spend": total_orders * random.uniform(500, 5000),
        "fraud_likelihood": profile["fraud_likelihood"],
    }


def generate_product(platform: str = "mixed") -> Dict:
    """Generate a random product."""
    if platform == "flipkart":
        categories = FLIPKART_CATEGORIES
    elif platform == "amazon":
        categories = AMAZON_CATEGORIES
    else:
        # Mix both
        categories = {**FLIPKART_CATEGORIES, **AMAZON_CATEGORIES}

    category_name = random.choice(list(categories.keys()))
    category = categories[category_name]

    price = random.uniform(*category["price_range"])

    # Determine price tier
    if price < 500:
        price_tier = "low"
    elif price < 2000:
        price_tier = "medium"
    elif price < 10000:
        price_tier = "high"
    else:
        price_tier = "premium"

    return {
        "category": category_name,
        "price": price,
        "price_tier": price_tier,
        "category_return_rate": category["return_rate"],
        "category_fraud_rate": category["fraud_rate"],
        "common_reasons": category["common_reasons"],
    }


def generate_return_request(
    buyer: Dict,
    product: Dict,
    is_fraud: bool = False
) -> Dict:
    """Generate a return request."""
    # Days since order
    if is_fraud:
        # Fraudsters often return late or very quickly
        if random.random() < 0.5:
            days_since_order = random.randint(25, 45)  # Near/past deadline
        else:
            days_since_order = random.randint(1, 3)  # Very quick return
    else:
        days_since_order = random.randint(3, 25)

    # Return reason
    if is_fraud:
        # Fraudsters use vague reasons
        reason = random.choice(["changed_mind", "not_as_described", "other"])
    else:
        reason = random.choice(product["common_reasons"])

    # Request timing
    hour = random.randint(0, 23)
    if is_fraud and random.random() < 0.3:
        hour = random.choice([1, 2, 3, 4, 23, 0])  # Odd hours

    day_of_week = random.randint(0, 6)

    return {
        "days_since_order": days_since_order,
        "return_reason": reason,
        "request_hour": hour,
        "request_day_of_week": day_of_week,
        "order_amount": product["price"],
    }


def generate_training_sample(platform: str = "mixed") -> Tuple[Dict, int]:
    """Generate a single training sample with label."""
    buyer = generate_buyer_profile()
    product = generate_product(platform)

    # Determine if this is a fraudulent return
    base_fraud_prob = buyer["fraud_likelihood"]
    category_fraud_prob = product["category_fraud_rate"]

    # Higher price = higher fraud attempt probability
    price_factor = min(product["price"] / 10000, 1.0) * 0.1

    fraud_probability = base_fraud_prob * 0.5 + category_fraud_prob * 0.3 + price_factor * 0.2
    is_fraud = random.random() < fraud_probability

    request = generate_return_request(buyer, product, is_fraud)

    # Calculate category risk score
    category_risk = product["category_return_rate"] * 0.5 + product["category_fraud_rate"] * 0.5

    features = {
        # Buyer features
        "buyer_return_rate": buyer["return_rate"],
        "buyer_total_orders": buyer["total_orders"],
        "buyer_total_returns": buyer["total_returns"],
        "buyer_avg_review_score": buyer["avg_review_score"],
        "buyer_account_age_days": buyer["account_age_days"],
        "buyer_total_spend": buyer["total_spend"],

        # Product features
        "product_return_rate": product["category_return_rate"],
        "product_category_risk": category_risk,
        "product_price": product["price"],
        "product_price_tier": product["price_tier"],

        # Request features
        "days_since_order": request["days_since_order"],
        "order_amount": request["order_amount"],
        "return_reason": request["return_reason"],
        "request_hour": request["request_hour"],
        "request_day_of_week": request["request_day_of_week"],
    }

    # Label: 1 = eligible (legitimate return), 0 = not eligible (fraud/abuse)
    label = 0 if is_fraud else 1

    return features, label


def generate_flipkart_amazon_dataset(
    n_samples: int = 10000,
    flipkart_ratio: float = 0.5
) -> Tuple[List[Dict], List[int]]:
    """
    Generate a dataset mixing Flipkart and Amazon patterns.

    Args:
        n_samples: Total number of samples
        flipkart_ratio: Ratio of Flipkart samples (rest are Amazon)

    Returns:
        Tuple of (features_list, labels_list)
    """
    np.random.seed(42)
    random.seed(42)

    data = []
    labels = []

    n_flipkart = int(n_samples * flipkart_ratio)
    n_amazon = n_samples - n_flipkart

    print(f"Generating {n_flipkart} Flipkart samples...")
    for _ in range(n_flipkart):
        features, label = generate_training_sample("flipkart")
        data.append(features)
        labels.append(label)

    print(f"Generating {n_amazon} Amazon samples...")
    for _ in range(n_amazon):
        features, label = generate_training_sample("amazon")
        data.append(features)
        labels.append(label)

    # Shuffle the data
    combined = list(zip(data, labels))
    random.shuffle(combined)
    data, labels = zip(*combined)

    # Print statistics
    fraud_count = sum(1 for l in labels if l == 0)
    legitimate_count = sum(1 for l in labels if l == 1)
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(labels)}")
    print(f"  Legitimate returns: {legitimate_count} ({legitimate_count/len(labels)*100:.1f}%)")
    print(f"  Fraudulent/abuse returns: {fraud_count} ({fraud_count/len(labels)*100:.1f}%)")

    return list(data), list(labels)


def generate_test_scenarios() -> List[Dict]:
    """Generate specific test scenarios for validation."""
    scenarios = [
        # Loyal customer, reasonable return
        {
            "name": "Loyal customer - clothing size issue",
            "features": {
                "buyer_return_rate": 0.05,
                "buyer_total_orders": 50,
                "buyer_total_returns": 2,
                "buyer_avg_review_score": 4.5,
                "buyer_account_age_days": 730,
                "buyer_total_spend": 50000,
                "product_return_rate": 0.25,
                "product_category_risk": 0.15,
                "product_price": 1500,
                "product_price_tier": "medium",
                "days_since_order": 5,
                "order_amount": 1500,
                "return_reason": "size_issue",
                "request_hour": 14,
                "request_day_of_week": 2,
            },
            "expected": "APPROVE",
        },
        # New customer, expensive item, quick return
        {
            "name": "New customer - expensive electronics",
            "features": {
                "buyer_return_rate": 0.20,
                "buyer_total_orders": 2,
                "buyer_total_returns": 0,
                "buyer_avg_review_score": 0,
                "buyer_account_age_days": 15,
                "buyer_total_spend": 30000,
                "product_return_rate": 0.08,
                "product_category_risk": 0.12,
                "product_price": 50000,
                "product_price_tier": "premium",
                "days_since_order": 2,
                "order_amount": 50000,
                "return_reason": "changed_mind",
                "request_hour": 3,
                "request_day_of_week": 0,
            },
            "expected": "REVIEW",
        },
        # High returner, late return
        {
            "name": "High returner - late return attempt",
            "features": {
                "buyer_return_rate": 0.45,
                "buyer_total_orders": 20,
                "buyer_total_returns": 9,
                "buyer_avg_review_score": 2.5,
                "buyer_account_age_days": 180,
                "buyer_total_spend": 15000,
                "product_return_rate": 0.15,
                "product_category_risk": 0.10,
                "product_price": 3000,
                "product_price_tier": "high",
                "days_since_order": 35,
                "order_amount": 3000,
                "return_reason": "not_as_described",
                "request_hour": 23,
                "request_day_of_week": 6,
            },
            "expected": "DENY",
        },
        # Potential fraud - jewelry
        {
            "name": "Suspicious - expensive jewelry return",
            "features": {
                "buyer_return_rate": 0.60,
                "buyer_total_orders": 5,
                "buyer_total_returns": 3,
                "buyer_avg_review_score": 1.5,
                "buyer_account_age_days": 30,
                "buyer_total_spend": 80000,
                "product_return_rate": 0.18,
                "product_category_risk": 0.20,
                "product_price": 25000,
                "product_price_tier": "premium",
                "days_since_order": 28,
                "order_amount": 25000,
                "return_reason": "other",
                "request_hour": 2,
                "request_day_of_week": 0,
            },
            "expected": "DENY",
        },
    ]

    return scenarios


if __name__ == "__main__":
    # Generate sample dataset
    data, labels = generate_flipkart_amazon_dataset(1000)

    # Print some samples
    print("\nSample data points:")
    for i in range(3):
        print(f"\nSample {i+1}:")
        print(f"  Features: {data[i]}")
        print(f"  Label: {'Legitimate' if labels[i] == 1 else 'Fraud/Abuse'}")
