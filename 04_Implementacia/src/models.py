"""
Dátové modely pre systém Zbierka.
Definuje entity pre používateľov, zberateľské predmety, cenovú históriu, pravidlá bota a notifikácie.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict

@dataclass
class User:
    id: str
    username: str
    email: str
    role: str = "COLLECTOR"
    currency: str = "EUR"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Category:
    id: int
    name: str
    parent_id: Optional[int] = None
    api_provider: Optional[str] = None

@dataclass
class Item:
    id: str
    user_id: str
    category_id: int
    name: str
    condition: str
    purchase_price: float
    estimated_value: float
    acquired_at: str
    photo_url: Optional[str] = None
    external_api_id: Optional[str] = None
    source_listing_id: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class PriceRecord:
    id: int
    item_id: str
    recorded_price: float
    source: str
    recorded_at: datetime = field(default_factory=datetime.now)

@dataclass
class BotFilter:
    id: int
    user_id: str
    keywords: str
    max_price: float
    exclude_words: List[str] = field(default_factory=list)
    target_market: str = "VINTED"
    is_active: bool = True

@dataclass
class MarketplaceListing:
    id: int
    external_id: str
    title: str
    price: float
    currency: str
    listing_url: str
    photo_url: str
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class Notification:
    id: int
    user_id: str
    listing: MarketplaceListing
    status: str = "PENDING"  # PENDING, ACCEPTED, DISMISSED
    sent_at: datetime = field(default_factory=datetime.now)
    action_taken_at: Optional[datetime] = None

@dataclass
class PortfolioSummary:
    user_id: str
    total_items: int
    total_purchase_price: float
    total_market_value: float
    total_roi_abs: float
    total_roi_pct: float
