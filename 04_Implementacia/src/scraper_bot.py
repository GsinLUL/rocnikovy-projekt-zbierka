"""
Autonómny monitorovací skript (Bot) pre online trhoviská (Vinted).
Nepretržite skenuje zverejnené ponuky, filtruje podľa kľúčových slov,
maximálnej ceny a negatívnych vylučovacích výrazov.
"""

from typing import List, Optional
import random
from datetime import datetime
from models import BotFilter, MarketplaceListing

class VintedMarketplaceBot:
    """
    Autonómny bot simulujúci nepretržité sledovanie inzerátov na trhovisku Vinted.
    """

    def __init__(self, filter_rule: BotFilter):
        self.filter_rule = filter_rule
        self.is_running = False

    def check_listing_matches(self, listing_title: str, price: float) -> bool:
        """
        Overí, či inzerát spĺňa pravidlá filtra zberateľa:
        1. Cena nesmie prekročiť cenový strop (max_price).
        2. Titulok musí obsahovať požadované kľúčové slová.
        3. Titulok nesmie obsahovať žiadne vylučovacie slovo (reprint, proxy, obal...).
        """
        # Kontrola ceny
        if price > self.filter_rule.max_price:
            return False

        title_lower = listing_title.lower()

        # Kontrola vylučovacích slov
        for exc in self.filter_rule.exclude_words:
            if exc.strip().lower() in title_lower:
                return False

        # Kontrola kľúčových slov
        kw_parts = [kw.strip().lower() for kw in self.filter_rule.keywords.split()]
        matches_all_keywords = all(kw in title_lower for kw in kw_parts)

        return matches_all_keywords

    def scan_marketplace_feed(self, simulated_feed: List[dict]) -> List[MarketplaceListing]:
        """
        Prehľadá dávku inzerátov a vráti len tie, ktoré presne spĺňajú podmienky filtra.
        """
        matched_listings: List[MarketplaceListing] = []

        for item in simulated_feed:
            if self.check_listing_matches(item["title"], item["price"]):
                matched = MarketplaceListing(
                    id=random.randint(1000, 9999),
                    external_id=item["external_id"],
                    title=item["title"],
                    price=item["price"],
                    currency=item.get("currency", "EUR"),
                    listing_url=item["listing_url"],
                    photo_url=item["photo_url"],
                    detected_at=datetime.now()
                )
                matched_listings.append(matched)

        return matched_listings
