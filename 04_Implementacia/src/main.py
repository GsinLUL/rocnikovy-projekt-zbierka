#!/usr/bin/env python3
"""
Hlavný demonštračný skript pre systém Zbierka.
Demonštruje:
1. Inicializáciu zberateľského portfólia a výpočet hodnoty.
2. Automatické obohatenie dát a fotografií cez verejné API (bez manuálneho vypisovania).
3. Autonómny beh monitorovacieho skriptu (bota) skenujúceho online trhovisko Vinted.
4. Vygenerovanie interaktívnej notifikácie pri detekcii ponuky.
5. KĽÚČOVÚ VLASTNOSŤ: Automatické zapísanie do databázy a okamžitý prepočet celkovej hodnoty zbierky.
"""

import sys
import time
from models import User, Item, BotFilter
from api_service import PublicCatalogApiService
from scraper_bot import VintedMarketplaceBot
from notification_engine import NotificationAndPortfolioEngine

def print_separator(title=""):
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("-" * 60)

def main():
    print_separator("SYSTÉM ZBIERKA – ROČNÍKOVÝ PROJEKT")
    print("Spúšťam integrovaný systém: Databázová aplikácia + Autonómny Bot")

    # 1. Používateľ a východiskový stav portfólia
    user = User(id="usr_001", username="zberatel_peter", email="peter@zbierka.sk")
    engine = NotificationAndPortfolioEngine(user_id=user.id)

    # Východiskové predmety v zbierke
    engine.add_initial_item(Item(
        id="item_01",
        user_id=user.id,
        category_id=1,
        name="Pikachu Illustrator Promo Card",
        condition="Near Mint",
        purchase_price=120.00,
        estimated_value=180.00,
        acquired_at="2026-01-15",
        photo_url="https://images.pokemontcg.io/promo/pikachu.png"
    ))
    engine.add_initial_item(Item(
        id="item_02",
        user_id=user.id,
        category_id=2,
        name="LEGO Star Wars UCS Millennium Falcon",
        condition="New in Box (Mint)",
        purchase_price=700.00,
        estimated_value=850.00,
        acquired_at="2026-03-20",
        photo_url="https://www.lego.com/cdn/cs/set/75192.jpg"
    ))

    print_separator("KROK 1: AKTUÁLNY STAV ZBERATEĽSKÉHO PORTFÓLIA")
    init_summary = engine.get_portfolio_summary()
    print(f"Používateľ:        {user.username} ({user.email})")
    print(f"Počet predmetov:   {init_summary.total_items} ks")
    print(f"Kúpna cena celkom: {init_summary.total_purchase_price:.2f} €")
    print(f"Trhová hodnota:    {init_summary.total_market_value:.2f} €")
    print(f"Zisk / ROI:        +{init_summary.total_roi_abs:.2f} € (+{init_summary.total_roi_pct:.1f} %)")

    # 2. Obohatenie cez verejné API
    print_separator("KROK 2: DOHĽADANIE A OBOHATENIE DÁT CEZ VEREJNÉ API")
    api_service = PublicCatalogApiService()
    query = "Charizard base set"
    print(f"Zberateľ zadal hľadaný výraz: '{query}'")
    api_result = api_service.enrich_item_data(query)

    if api_result["success"]:
        data = api_result["data"]
        print(f"[✓] {api_result['message']}")
        print(f"    - Oficiálny názov: {data['name']}")
        print(f"    - Edícia / Rok:    {data['publisher']} ({data['release_year']})")
        print(f"    - Rarita:          {data['rarity']}")
        print(f"    - Foto URL:        {data['photo_url']}")
        print(f"    - Odhadovaná cena: {data['recommended_market_price']:.2f} €")
        print("    -> Používateľ nemusel manuálne vypisovať žiadne technické atribúty!")

    # 3. Autonómny bot a pravidlá skenovania
    print_separator("KROK 3: AKTIVÁCIA AUTONÓMNEHO MONITOROVACIEHO BOTA")
    bot_filter = BotFilter(
        id=101,
        user_id=user.id,
        keywords="Charizard base set",
        max_price=150.00,  # Hľadáme výhodnú ponuku do 150 €
        exclude_words=["reprint", "proxy", "obal"],
        target_market="VINTED"
    )
    bot = VintedMarketplaceBot(filter_rule=bot_filter)
    print(f"Bot aktivovaný s pravidlami:")
    print(f"  • Kľúčové slová:  '{bot_filter.keywords}'")
    print(f"  • Cenový strop:   max {bot_filter.max_price:.2f} €")
    print(f"  • Vylučovacie:    {bot_filter.exclude_words}")
    print(f"  • Trhovisko:      {bot_filter.target_market}")

    # Simulovaný zoznam nových inzerátov na trhovisku Vinted
    simulated_vinted_feed = [
        {
            "external_id": "vinted_981",
            "title": "Charizard base set obal na kartu",
            "price": 10.00,
            "listing_url": "https://vinted.sk/items/981",
            "photo_url": "https://vinted.sk/photos/981.jpg"
        },
        {
            "external_id": "vinted_982",
            "title": "Charizard base set holo karta 1999 original",
            "price": 85.00,  # Super cena! Spĺňa všetky kritériá!
            "listing_url": "https://vinted.sk/items/982",
            "photo_url": "https://vinted.sk/photos/982_front.jpg"
        },
        {
            "external_id": "vinted_983",
            "title": "Charizard base set psa 10",
            "price": 2500.00,  # Príliš drahé (prekračuje 150 € strop)
            "listing_url": "https://vinted.sk/items/983",
            "photo_url": "https://vinted.sk/photos/983.jpg"
        }
    ]

    print("\nBot skenuje prichádzajúce ponuky na trhovisku...")
    matched = bot.scan_marketplace_feed(simulated_vinted_feed)
    print(f"Sken dokončený. Nájdených vyhovujúcich inzerátov: {len(matched)}")

    if not matched:
        print("Žiadna nová ponuka nespĺňa kritériá.")
        return

    best_match = matched[0]
    print(f"[!] DETEGOVANÝ RELEVANTNÝ INZERÁT: '{best_match.title}'")
    print(f"    Cena: {best_match.price:.2f} € | Odkaz: {best_match.listing_url}")

    # 4. Doručenie interaktívnej notifikácie
    print_separator("KROK 4: VYGENEROVANIE INTERAKTÍVNEJ NOTIFIKÁCIE")
    notif = engine.dispatch_interactive_notification(best_match)
    print(f"Notifikácia #{notif.id} doručená do zariadenia používateľa:")
    print(f"┌─────────────────────────────────────────────────────────────┐")
    print(f"│ 🔔 NOVÁ PONUKA NA VINTED: {best_match.title[:30]}...         │")
    print(f"│ Cena: {best_match.price:.2f} € (Odhadovaná trhová hodnota: ~125.00 €) │")
    print(f"│ [ Akcia: Kliknutie na 'PRIDAŤ DO ZBIERKY' ]                │")
    print(f"└─────────────────────────────────────────────────────────────┘")

    # 5. Kľúčová vlastnosť: Používateľská interakcia a okamžitý prepočet
    print_separator("KROK 5: INTERAKCIA S NOTIFIKÁCIOU A AUTOMATICKÝ ZÁPIS")
    print("Používateľ klikol na interaktívne tlačidlo: [ PRIDAŤ DO ZBIERKY ]")
    print("Spracovávam transakčný zápis a prepočítavam celkovú hodnotu...")

    result = engine.handle_quick_add_interaction(notification_id=notif.id)

    if result["success"]:
        print(f"\n[✓] {result['message']}")
        print(f"\nPOROVNANIE HODNOTY ZBIERKY PRED A PO INTERAKCII:")
        before = result["summary_before"]
        after = result["summary_after"]

        print(f"{'Ukazovateľ':<25} | {'Pred pridaním':<15} | {'Po pridaní':<15} | {'Rozdiel'}")
        print("-" * 75)
        print(f"{'Počet položiek':<25} | {before.total_items:<15} | {after.total_items:<15} | +1 ks")
        print(f"{'Kúpna cena celkom':<25} | {before.total_purchase_price:>12.2f} € | {after.total_purchase_price:>12.2f} € | +{best_match.price:.2f} €")
        print(f"{'Trhová hodnota zbierky':<25} | {before.total_market_value:>12.2f} € | {after.total_market_value:>12.2f} € | +{result['added_item'].estimated_value:.2f} €")
        print(f"{'Zisk (ROI) celkom':<25} | {before.total_roi_abs:>12.2f} € | {after.total_roi_abs:>12.2f} € | +{result['added_item'].estimated_value - best_match.price:.2f} €")
        print(f"{'Zhodnotenie v %':<25} | {before.total_roi_pct:>12.1f} % | {after.total_roi_pct:>12.1f} % |")

    print_separator("DEMONŠTRÁCIA ÚSPEŠNE DOKONČENÁ")

if __name__ == "__main__":
    main()
