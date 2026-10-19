#!/usr/bin/env python3
"""
Automatizované jednotkové a integračné testy pre systém Zbierka.
Overuje biznis logiku portfólia, obohatenie cez verejné API,
filtrovanie autonómneho bota a automatický prepočet hodnoty zbierky.
"""

import unittest
import sys
import os

# Pridanie cesty k implementácii
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../04_Implementacia/src')))

from models import User, Item, BotFilter, MarketplaceListing
from api_service import PublicCatalogApiService
from scraper_bot import VintedMarketplaceBot
from notification_engine import NotificationAndPortfolioEngine

class TestCollectorSystem(unittest.TestCase):

    def setUp(self):
        self.user = User(id="test_user", username="tester", email="test@zbierka.sk")
        self.engine = NotificationAndPortfolioEngine(user_id=self.user.id)
        self.api = PublicCatalogApiService()

    def test_api_enrichment_success(self):
        """TC-003: Overenie automatického načítania metadát z verejného API."""
        result = self.api.enrich_item_data("Charizard base set")
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["data"])
        self.assertEqual(result["data"]["release_year"], 1999)
        self.assertTrue("https://" in result["data"]["photo_url"])
        self.assertGreater(result["data"]["recommended_market_price"], 0)

    def test_api_enrichment_unknown_item(self):
        """TC-004: Overenie správania pri neznámom predmete."""
        result = self.api.enrich_item_data("Neexistujuci Predmet XYZ 999")
        self.assertFalse(result["success"])
        self.assertIsNone(result["data"])

    def test_bot_filtering_logic(self):
        """TC-005: Overenie filtračnej logiky autonómneho bota."""
        filter_rule = BotFilter(
            id=1,
            user_id="test_user",
            keywords="Charizard base set",
            max_price=150.00,
            exclude_words=["reprint", "proxy", "obal"],
            target_market="VINTED"
        )
        bot = VintedMarketplaceBot(filter_rule=filter_rule)

        # 1. Platný inzerát
        self.assertTrue(bot.check_listing_matches("Charizard base set holo karta 1999", 85.00))
        # 2. Prekročená cena
        self.assertFalse(bot.check_listing_matches("Charizard base set holo karta 1999", 250.00))
        # 3. Vylučovacie slovo "obal"
        self.assertFalse(bot.check_listing_matches("Charizard base set obal na kartu", 10.00))
        # 4. Vylučovacie slovo "proxy"
        self.assertFalse(bot.check_listing_matches("Charizard base set proxy karta", 5.00))
        # 5. Nezhodné kľúčové slová
        self.assertFalse(bot.check_listing_matches("Pikachu base set original", 30.00))

    def test_quick_add_and_instant_recalculation(self):
        """
        TC-007: Overenie KĽÚČOVEJ VLASTNOSTI:
        Zápis z interaktívnej notifikácie priamo do databázy a okamžitý prepočet hodnoty zbierky.
        """
        # Počiatočný stav: 1 položka za 100 €, hodnota 150 €
        self.engine.add_initial_item(Item(
            id="item_init",
            user_id="test_user",
            category_id=1,
            name="Základná karta",
            condition="Good",
            purchase_price=100.00,
            estimated_value=150.00,
            acquired_at="2026-01-01"
        ))
        initial_summary = self.engine.get_portfolio_summary()
        self.assertEqual(initial_summary.total_items, 1)
        self.assertEqual(initial_summary.total_purchase_price, 100.00)
        self.assertEqual(initial_summary.total_market_value, 150.00)

        # Bot vytvorí inzerát a doručí notifikáciu
        listing = MarketplaceListing(
            id=555,
            external_id="v_555",
            title="Charizard base set holo",
            price=80.00,
            currency="EUR",
            listing_url="https://vinted.sk/items/555",
            photo_url="https://vinted.sk/photo.jpg"
        )
        notif = self.engine.dispatch_interactive_notification(listing)
        self.assertEqual(notif.status, "PENDING")

        # Používateľ klikne na "Pridať do zbierky"
        result = self.engine.handle_quick_add_interaction(notification_id=notif.id)
        self.assertTrue(result["success"])

        # Overenie zápisu v databáze
        self.assertEqual(len(self.engine.database_items), 2)
        added = result["added_item"]
        self.assertEqual(added.purchase_price, 80.00)
        self.assertEqual(added.source_listing_id, 555)

        # Overenie okamžitého prepočtu celkovej hodnoty zbierky
        new_summary = result["summary_after"]
        self.assertEqual(new_summary.total_items, 2)
        self.assertEqual(new_summary.total_purchase_price, 180.00)
        self.assertGreater(new_summary.total_market_value, 150.00)
        self.assertEqual(new_summary.total_market_value, round(150.00 + added.estimated_value, 2))

        # Overenie prevencie duplicitného kliknutia
        duplicate_attempt = self.engine.handle_quick_add_interaction(notification_id=notif.id)
        self.assertFalse(duplicate_attempt["success"])

if __name__ == "__main__":
    unittest.main()
