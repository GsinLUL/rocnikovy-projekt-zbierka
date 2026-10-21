"""
app.py - Hlavná aplikácia pre zberateľský portál Zbierka & Vinted Snajper
Spája databázovú správu portfólia, automatické API dopĺňanie a autonómneho bota.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import sqlite3
from datetime import datetime

import database
import api_catalog
import telegram_service

app = Flask(__name__)
app.secret_key = "zbierka-vinted-collector-secret-key-2026"

BOT_DIR = os.path.join(os.path.dirname(__file__), "bot")
CONFIG_PATH = os.path.join(BOT_DIR, "config.json")
STATUS_PATH = os.path.join(BOT_DIR, "bot_status.json")

# Inicializácia databázy pri štarte
database.init_db()

@app.route("/")
def index():
    """Hlavná stránka s kompletným Apple/Vinted zberateľským rozhraním."""
    summary = database.get_portfolio_summary()
    items = database.get_all_items()
    categories = sorted(list(set(item["category"] for item in items)))
    vinted_categories = database.get_vinted_categories_with_counts()
    telegram_creds = telegram_service.get_telegram_credentials()
    api_settings = api_catalog.get_collector_api_settings()

    # Načítanie aktívnych vyhľadávaní bota
    searches = []
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                searches = config_data.get("searches", [])
        except Exception:
            searches = []

    return render_template(
        "index.html",
        summary=summary,
        items=items,
        categories=categories,
        searches=searches,
        vinted_categories=vinted_categories,
        telegram_creds=telegram_creds,
        api_settings=api_settings
    )

# ── API pre Zbierku (Portfólio) ──────────────────────────────────────────────────

@app.route("/api/portfolio", methods=["GET"])
def api_portfolio():
    """Vráti položky zbierky a aktuálny prepočet celkovej hodnoty."""
    category = request.args.get("category", "")
    search = request.args.get("search", "")
    sort_by = request.args.get("sort_by", "newest")

    items = database.get_all_items(search_query=search, category=category, sort_by=sort_by)
    summary = database.get_portfolio_summary()
    return jsonify({
        "items": items,
        "summary": summary
    })

@app.route("/api/items/<int:item_id>", methods=["GET"])
def api_get_item(item_id):
    """Vráti detail konkrétneho predmetu s galériou fotografií a cenovou históriou."""
    item = database.get_item(item_id)
    if not item:
        return jsonify({"success": False, "error": "Položka neexistuje"}), 404
    return jsonify(item)

@app.route("/api/items", methods=["POST"])
def api_add_item():
    """Pridá novú položku do zbierky s podporou viacerých fotografií a okamžite prepočíta celkovú hodnotu."""
    data = request.json or request.form.to_dict()
    if not data or not data.get("name") or not data.get("purchase_price"):
        return jsonify({"success": False, "error": "Chýba názov alebo kúpna cena"}), 400

    new_id = database.add_item_to_collection(data)
    new_summary = database.get_portfolio_summary()

    return jsonify({
        "success": True,
        "item_id": new_id,
        "summary": new_summary,
        "message": f"Položka '{data['name']}' bola pridaná do zbierky!"
    })

@app.route("/api/items/<int:item_id>", methods=["PUT"])
def api_update_item(item_id):
    """Upraví existujúcu položku (cena, stav, fotky, poznámky) a prepočíta hodnotu."""
    data = request.json or request.form.to_dict()
    if not data or not data.get("name") or not data.get("purchase_price"):
        return jsonify({"success": False, "error": "Chýba názov alebo kúpna cena"}), 400

    ok = database.update_item(item_id, data)
    if not ok:
        return jsonify({"success": False, "error": "Položka neexistuje"}), 404

    updated_item = database.get_item(item_id)
    new_summary = database.get_portfolio_summary()

    return jsonify({
        "success": True,
        "item": updated_item,
        "summary": new_summary,
        "message": f"Položka '{data['name']}' bola úspešne upravená!"
    })

@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def api_delete_item(item_id):
    """Zmaže položku zo zbierky a prepočíta hodnotu."""
    database.delete_item(item_id)
    new_summary = database.get_portfolio_summary()
    return jsonify({
        "success": True,
        "summary": new_summary,
        "message": "Položka bola vymazaná zo zbierky."
    })

@app.route("/api/chart", methods=["GET"])
def api_chart():
    """Vráti dáta pre interaktívny graf vývoja trhovej hodnoty."""
    return jsonify(database.get_history_chart_data())

# ── API pre verejný katalóg (Automatické dopĺňanie z PriceCharting, Pokémon, Wiki, Books) ──

@app.route("/api/catalog/search", methods=["GET"])
def api_catalog_search():
    """
    Vyhľadávanie vo verejných API:
    Dopĺňa metadáta, odhadované trhové ceny a galériu fotografií.
    """
    q = request.args.get("q", "")
    source = request.args.get("source", "all")
    results = api_catalog.search_catalog_api(q, source=source)
    return jsonify(results)

@app.route("/api/settings/apis", methods=["GET"])
def api_get_settings():
    """Vráti zoznam zapnutých verejných API a konfiguráciu."""
    return jsonify(api_catalog.get_collector_api_settings())

@app.route("/api/settings/apis", methods=["POST"])
def api_save_settings():
    """Uloží nastavenia zapnutých verejných API."""
    data = request.json or {}
    ok = api_catalog.save_collector_api_settings(data)
    if ok:
        return jsonify({"success": True, "message": "Nastavenia verejných API boli úspešne uložené."})
    return jsonify({"success": False, "error": "Chyba zápisu nastavení."}), 500

@app.route("/api/settings/apis/test", methods=["POST"])
def api_test_settings():
    """Otestuje dostupnosť vybraného verejného API."""
    data = request.json or {}
    api_name = data.get("api_name") or data.get("api", "pricecharting")
    
    # Rýchly test podľa názvu API
    try:
        if api_name in ["pokemon", "pokemontcg"]:
            cards = api_catalog.query_pokemon_tcg_api("pikachu", limit=1)
            return jsonify({"success": True, "api": "Pokemon TCG API", "status": "Online (200 OK)", "count": len(cards)})
        elif api_name == "wikipedia":
            wiki = api_catalog.query_wikipedia_api("PlayStation", limit=1)
            return jsonify({"success": True, "api": "Wikipedia / Wikimedia API", "status": "Online (200 OK)", "count": len(wiki)})
        elif api_name == "openlibrary":
            books = api_catalog.query_openlibrary_api("dune", limit=1)
            return jsonify({"success": True, "api": "Open Library Books API", "status": "Online (200 OK)", "count": len(books)})
        else: # pricecharting
            items = api_catalog.search_catalog_api("PS2", source="pricecharting")
            return jsonify({"success": True, "api": "PriceCharting Retro DB", "status": "Online & Aktívny", "count": len(items)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

# ── API pre Vinted Snajpera (Bot & Inzeráty) ─────────────────────────────────────

@app.route("/api/vinted/listings", methods=["GET"])
def api_vinted_listings():
    """Načíta inzeráty zachytené botom s podporou filtrovania, triedenia a dynamických časov."""
    search_name = request.args.get("search_name", "all")
    search_query = request.args.get("q", "").strip()
    sort_by = request.args.get("sort_by", "newest")
    limit = int(request.args.get("limit", 60))

    listings = database.get_vinted_listings(
        search_name=search_name,
        search_query=search_query,
        sort_by=sort_by,
        limit=limit
    )
    categories = database.get_vinted_categories_with_counts()
    creds = telegram_service.get_telegram_credentials()

    return jsonify({
        "listings": listings,
        "categories": categories,
        "telegram": {
            "is_configured": creds["is_configured"],
            "chat_id": creds["chat_id"]
        }
    })

# ── API pre Telegram Integráciu (Notifikácie) ────────────────────────────────────

@app.route("/api/telegram/status", methods=["GET"])
def api_telegram_status():
    """Vráti informácie o stave prepojenia s Telegramom."""
    creds = telegram_service.get_telegram_credentials()
    return jsonify({
        "is_configured": creds["is_configured"],
        "chat_id": creds["chat_id"],
        "token_preview": (creds["token"][:7] + "..." + creds["token"][-4:]) if creds["token"] else ""
    })

@app.route("/api/telegram/save", methods=["POST"])
def api_telegram_save():
    """Uloží Telegram Bot Token a Chat ID."""
    data = request.json or {}
    token = data.get("token", "").strip()
    chat_id = data.get("chat_id", "").strip()

    if not token or not chat_id:
        return jsonify({"success": False, "error": "Zadajte prosím Telegram Bot Token aj Chat ID"}), 400

    ok = telegram_service.save_telegram_credentials(token, chat_id)
    if ok:
        return jsonify({"success": True, "message": "Telegram notifikácie boli úspešne prepojené!"})
    else:
        return jsonify({"success": False, "error": "Chyba pri ukladaní nastavení."}), 500

@app.route("/api/telegram/test", methods=["POST"])
def api_telegram_test():
    """Otestuje odoslanie správy do Telegram chatu s reálnym formátom inzerátu."""
    data = request.json or {}
    title = data.get("title", "Sony PlayStation 2 Slim (Testovacia notifikácia)")
    price = float(data.get("price", 39.0))
    url = data.get("url", "https://www.vinted.sk/catalog?search_text=ps2")
    image_url = data.get("image_url", "https://images1.vinted.net/t/05_024b4_8x1hKvdQ1rDps8T1o7BqC3N9/310x430/1715423891.jpeg?s=1")
    search_name = data.get("search_name", "PS2")

    res = telegram_service.send_telegram_notification(
        title=title,
        price_eur=price,
        url=url,
        image_url=image_url,
        search_name=search_name,
        custom_badge="⚡ TEST Z WEBU"
    )
    return jsonify(res)

@app.route("/api/vinted/simulate-deal", methods=["POST"])
def api_simulate_deal():
    """
    Simuluje zachytenie nového inzerátu Vinted Snajperom:
    1. Zapíše inzerát do databázy bota (vinted_bot.db) s aktuálnym časom NOW.
    2. Ak je Telegram nakonfigurovaný, automaticky pošle správu do Telegram chatu.
    3. Okamžite vráti položku webovej stránke pre živé zobrazenie (pred 1 sekundou).
    """
    import random
    samples = [
        {
            "title": "Sony PlayStation 2 Slim SCPH-77004 + 2 ovládače a memory karta",
            "price": "38,00 €",
            "numeric_price": 38.00,
            "search_name": "PS2",
            "image_url": "https://images1.vinted.net/t/05_024b4_8x1hKvdQ1rDps8T1o7BqC3N9/310x430/1715423891.jpeg?s=1",
            "url": "https://www.vinted.sk/catalog?search_text=ps2&order=newest_first"
        },
        {
            "title": "Apple iPod Classic 7th Gen 160GB Space Gray TOP stav bez škrabancov",
            "price": "65,00 €",
            "numeric_price": 65.00,
            "search_name": "Ipod",
            "image_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
            "url": "https://www.vinted.sk/catalog?search_text=ipod&order=newest_first"
        },
        {
            "title": "Nintendo Game Boy Advance SP (Tribal Edition) s nabíjačkou",
            "price": "55,00 €",
            "numeric_price": 55.00,
            "search_name": "Nintendo",
            "image_url": "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?w=600&auto=format&fit=crop&q=80",
            "url": "https://www.vinted.sk/catalog?search_text=nintendo&order=newest_first"
        },
        {
            "title": "Sony Cyber-shot DSC-W55 Retro strieborný 7.2MPx funkčný",
            "price": "24,00 €",
            "numeric_price": 24.00,
            "search_name": "sony kamera",
            "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
            "url": "https://www.vinted.sk/catalog?search_text=sony+kamera&order=newest_first"
        },
        {
            "title": "Xbox 360 Slim 250GB s bezdrôtovým gamepadom",
            "price": "42,00 €",
            "numeric_price": 42.00,
            "search_name": "Xbox",
            "image_url": "https://images.unsplash.com/photo-1605901309584-818e25960a8f?w=600&auto=format&fit=crop&q=80",
            "url": "https://www.vinted.sk/catalog?search_text=xbox&order=newest_first"
        }
    ]
    picked = random.choice(samples)
    now_dt = datetime.utcnow()
    item_id = str(random.randint(10150000000, 10199999999))
    item_data = {
        "search_name": picked["search_name"],
        "item_id": item_id,
        "title": picked["title"],
        "price": picked["price"],
        "url": picked["url"],
        "image_url": picked["image_url"],
        "added_at": now_dt.isoformat() + "Z"
    }

    # 1. Zápis do databázy bota
    database.add_vinted_listing(item_data)

    # 2. Odoslanie notifikácie na Telegram
    tg_res = telegram_service.send_telegram_notification(
        title=item_data["title"],
        price_eur=picked["numeric_price"],
        url=item_data["url"],
        image_url=item_data["image_url"],
        search_name=item_data["search_name"],
        custom_badge="⚡ NOVÝ ÚLOVOK"
    )

    # 3. Dáta pre okamžité pridanie do živého feedu na webe
    item_data["numeric_price"] = picked["numeric_price"]
    item_data["buyer_protection_price"] = telegram_service.calculate_buyer_protection(picked["numeric_price"])
    item_data["buyer_protection_str"] = f"{item_data['buyer_protection_price']:.2f}".replace('.', ',') + " €"
    item_data["price_formatted"] = picked["price"]
    item_data["added_at_ts"] = int(now_dt.timestamp() * 1000)
    item_data["already_added"] = False
    item_data["is_live_demo"] = True

    return jsonify({
        "success": True,
        "item": item_data,
        "telegram_sent": tg_res.get("success", False),
        "telegram_info": tg_res,
        "message": f"Nový inzerát '{item_data['title'][:35]}...' bol zachytený a zaevidovaný!"
    })

@app.route("/api/vinted/quick-add", methods=["POST"])
def api_quick_add():
    """
    KĽÚČOVÁ VLASTNOSŤ PROJEKTU:
    Po interakcii s inzerátom / notifikáciou sa daný predmet priamo zapíše
    do používateľovej databázy a okamžite sa prepočíta celková hodnota zbierky.
    """
    data = request.json
    if not data or not data.get("title"):
        return jsonify({"success": False, "error": "Chýbajú údaje o inzeráte"}), 400

    title = data.get("title")
    price = float(data.get("price", 0.0))
    # Pokus o inteligentný odhad trhovej hodnoty z katalógu
    enrichment = api_catalog.get_item_enrichment(title)

    estimated_value = float(data.get("estimated_value", 0.0))
    if estimated_value <= 0:
        if enrichment and enrichment.get("estimated_value"):
            estimated_value = enrichment["estimated_value"]
        else:
            estimated_value = round(price * 1.35, 2)

    category = data.get("category")
    if not category:
        category = enrichment.get("category", "Elektronika & Hry") if enrichment else "Konzoly & Hry"

    photo_url = data.get("photo_url")
    if not photo_url and enrichment:
        photo_url = enrichment.get("photo_url")

    item_data = {
        "name": title,
        "category": category,
        "condition": data.get("condition", "Veľmi dobrý (Vinted)"),
        "purchase_price": price,
        "estimated_value": estimated_value,
        "photo_url": photo_url,
        "source": "Vinted Snajper",
        "source_url": data.get("url", ""),
        "vinted_item_id": data.get("item_id"),
        "notes": f"Automaticky pridané z Vintedu ({data.get('search_name', 'Sledovanie')}) dňa {datetime.now().strftime('%d.%m.%Y %H:%M')}."
    }

    new_id = database.add_item_to_collection(item_data)
    new_summary = database.get_portfolio_summary()

    return jsonify({
        "success": True,
        "item_id": new_id,
        "summary": new_summary,
        "added_item": item_data,
        "message": f"Inzerát '{title[:40]}...' bol úspešne zapísaný do zbierky! Nová hodnota: {new_summary['total_value']:.2f} €."
    })

@app.route("/api/bot/status", methods=["GET"])
def api_bot_status():
    """Zistí stav bota a načítané nastavenia."""
    status = {
        "is_running": False,
        "searches_count": 0,
        "last_scan": "Neznámy",
        "bot_name": "Vinted Snajper"
    }

    if os.path.exists(STATUS_PATH):
        try:
            with open(STATUS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                status.update(data)
        except Exception:
            pass

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                status["searches_count"] = len(cfg.get("searches", []))
                status["bot_name"] = cfg.get("settings", {}).get("bot_name", "Vinted Snajper")
        except Exception:
            pass

    return jsonify(status)

@app.route("/api/bot/searches", methods=["POST"])
def api_add_bot_search():
    """Pridá nové hľadané kľúčové slovo do config.json bota."""
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "error": "Zadajte názov hľadania"}), 400

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {"settings": {}, "searches": []}
    else:
        cfg = {"settings": {}, "searches": []}

    encoded = name.replace(" ", "+")
    new_entry = {
        "name": name,
        "url": f"https://www.vinted.sk/catalog?search_text={encoded}&order=newest_first",
        "keywords": []
    }
    cfg.setdefault("searches", []).append(new_entry)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

    return jsonify({"success": True, "message": f"Hľadanie '{name}' bolo pridané pre Vinted Snajpera."})

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🚀 ZBIERKA & VINTED SNAJPER – Portfólio a autonómny bot")
    print("  🌐 Webová aplikácia beží na: http://127.0.0.1:5001")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5001, debug=True)
