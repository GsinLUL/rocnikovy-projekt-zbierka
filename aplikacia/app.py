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
        searches=searches
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

@app.route("/api/items", methods=["POST"])
def api_add_item():
    """Pridá novú položku do zbierky a okamžite prepočíta celkovú hodnotu."""
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

# ── API pre verejný katalóg (Automatické dopĺňanie metadát a fotografií) ─────────

@app.route("/api/catalog/search", methods=["GET"])
def api_catalog_search():
    """
    Vyhľadávanie v katalógu: automatické dopĺňanie metadát a fotografií.
    Eliminuje nutnosť manuálneho vypisovania údajov.
    """
    q = request.args.get("q", "")
    results = api_catalog.search_catalog_api(q)
    return jsonify(results)

# ── API pre Vinted Snajpera (Bot & Inzeráty) ─────────────────────────────────────

@app.route("/api/vinted/listings", methods=["GET"])
def api_vinted_listings():
    """Načíta inzeráty zachytené botom s príznakom či sú už pridané v zbierke."""
    search_name = request.args.get("search_name", "all")
    listings = database.get_vinted_listings(search_name=search_name, limit=100)
    return jsonify(listings)

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
