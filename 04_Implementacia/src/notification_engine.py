"""
Notifikačný engine a integrácia automatického pridávania do databázy.
Kľúčová vlastnosť systému:
Po interakcii s notifikáciou (kliknutie na tlačidlo 'Pridať') zapíše položku
priamo do databázy a okamžite v reálnom čase prepočíta celkovú hodnotu zbierky.
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid
from models import Item, Notification, MarketplaceListing, PortfolioSummary

class NotificationAndPortfolioEngine:
    """
    Integruje autonómneho bota s centrálnym databázovým portfóliom zberateľa.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        # Simulovaná databáza predmetov používateľa
        self.database_items: List[Item] = []
        # Zoznam vygenerovaných notifikácií
        self.notifications: List[Notification] = []

    def add_initial_item(self, item: Item):
        """Pomocná metóda pre naplnenie východiskového stavu zbierky."""
        self.database_items.append(item)

    def dispatch_interactive_notification(self, listing: MarketplaceListing) -> Notification:
        """
        Vygeneruje a doručí interaktívnu notifikáciu pre zberateľa.
        """
        notification = Notification(
            id=len(self.notifications) + 1,
            user_id=self.user_id,
            listing=listing,
            status="PENDING",
            sent_at=datetime.now()
        )
        self.notifications.append(notification)
        return notification

    def handle_quick_add_interaction(self, notification_id: int) -> Dict[str, any]:
        """
        KĽÚČOVÁ FUNKCIONALITA:
        Spracuje používateľskú interakciu 'Pridať do zbierky' z notifikácie.
        1. Overí platnosť notifikácie.
        2. Zapíše nájdený predmet priamo do používateľovej databázy.
        3. Okamžite prepočíta celkovú hodnotu zberateľovho portfólia.
        """
        notif: Optional[Notification] = None
        for n in self.notifications:
            if n.id == notification_id and n.status == "PENDING":
                notif = n
                break

        if not notif:
            return {
                "success": False,
                "message": f"Notifikácia #{notification_id} nebola nájdená alebo už bola spracovaná."
            }

        # Označenie notifikácie ako spracovanej
        notif.status = "ACCEPTED"
        notif.action_taken_at = datetime.now()

        # Vytvorenie a zápis nového predmetu do databázy
        listing = notif.listing
        new_item = Item(
            id=str(uuid.uuid4())[:8],
            user_id=self.user_id,
            category_id=1,  # Priradenie kategórie
            name=listing.title,
            condition="Nájdené na trhovisku (Vinted)",
            purchase_price=listing.price,
            # Odhadovaná hodnota položky (trhová hodnota býva vyššia než výhodná kúpna cena)
            estimated_value=round(listing.price * 1.45, 2),
            acquired_at=datetime.now().strftime("%Y-%m-%d"),
            photo_url=listing.photo_url,
            source_listing_id=listing.id,
            notes=f"Automaticky pridané z notifikácie Vinted dňa {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        self.database_items.append(new_item)

        # OKAMŽITÝ PREPOČET HODNOTY ZBIERKY
        summary_before = self.get_portfolio_summary_excluding(new_item.id)
        summary_after = self.get_portfolio_summary()

        return {
            "success": True,
            "added_item": new_item,
            "summary_before": summary_before,
            "summary_after": summary_after,
            "value_difference": round(summary_after.total_market_value - summary_before.total_market_value, 2),
            "message": (
                f"Predmet '{new_item.name}' bol úspešne zapísaný do databázy! "
                f"Celková hodnota zbierky bola okamžite prepočítaná na {summary_after.total_market_value:.2f} € "
                f"(nárast o +{new_item.estimated_value:.2f} €)."
            )
        }

    def get_portfolio_summary(self) -> PortfolioSummary:
        """
        Vypočíta a agreguje celkovú kúpnu cenu, celkovú trhovú hodnotu a zisk (ROI).
        """
        total_items = len(self.database_items)
        total_purchase = sum(item.purchase_price for item in self.database_items)
        total_market = sum(item.estimated_value for item in self.database_items)
        roi_abs = total_market - total_purchase
        roi_pct = (roi_abs / total_purchase * 100.0) if total_purchase > 0 else 0.0

        return PortfolioSummary(
            user_id=self.user_id,
            total_items=total_items,
            total_purchase_price=round(total_purchase, 2),
            total_market_value=round(total_market, 2),
            total_roi_abs=round(roi_abs, 2),
            total_roi_pct=round(roi_pct, 2)
        )

    def get_portfolio_summary_excluding(self, exclude_item_id: str) -> PortfolioSummary:
        """Vypočíta súhrn bez konkrétnej položky (pre zobrazenie zmeny pred/po)."""
        filtered = [item for item in self.database_items if item.id != exclude_item_id]
        total_items = len(filtered)
        total_purchase = sum(item.purchase_price for item in filtered)
        total_market = sum(item.estimated_value for item in filtered)
        roi_abs = total_market - total_purchase
        roi_pct = (roi_abs / total_purchase * 100.0) if total_purchase > 0 else 0.0

        return PortfolioSummary(
            user_id=self.user_id,
            total_items=total_items,
            total_purchase_price=round(total_purchase, 2),
            total_market_value=round(total_market, 2),
            total_roi_abs=round(roi_abs, 2),
            total_roi_pct=round(roi_pct, 2)
        )
