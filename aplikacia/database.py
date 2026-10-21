"""
database.py - Databázová vrstva pre správu zberateľského portfólia
Spravuje zberateľské predmety, cenovú históriu a prepojenie s databázou Vinted Snajpera.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "zbierka.db")
BOT_DB_FILE = os.path.join(os.path.dirname(__file__), "bot", "vinted_bot.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

import json

def init_db():
    """Inicializuje tabuľky pre portfólio a predvyplní štartovacie položky ak je databáza prázdna."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        condition TEXT NOT NULL,
        purchase_price REAL NOT NULL,
        estimated_value REAL NOT NULL,
        photo_url TEXT,
        photos TEXT DEFAULT '[]',
        brand TEXT DEFAULT '',
        release_year INTEGER DEFAULT NULL,
        market_source TEXT DEFAULT 'PriceCharting',
        source TEXT DEFAULT 'Manuálne',
        source_url TEXT,
        vinted_item_id TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        record_date TEXT NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
    );
    """)

    # Migrácia: overenie či existujú novšie stĺpce (photos, brand, release_year, market_source)
    cursor.execute("PRAGMA table_info(items)")
    existing_cols = set(row[1] for row in cursor.fetchall())
    if "photos" not in existing_cols:
        cursor.execute("ALTER TABLE items ADD COLUMN photos TEXT DEFAULT '[]'")
    if "brand" not in existing_cols:
        cursor.execute("ALTER TABLE items ADD COLUMN brand TEXT DEFAULT ''")
    if "release_year" not in existing_cols:
        cursor.execute("ALTER TABLE items ADD COLUMN release_year INTEGER DEFAULT NULL")
    if "market_source" not in existing_cols:
        cursor.execute("ALTER TABLE items ADD COLUMN market_source TEXT DEFAULT 'PriceCharting'")

    conn.commit()
    conn.close()

def get_all_items(search_query: str = "", category: str = "", sort_by: str = "newest") -> List[Dict[str, Any]]:
    """Vráti zoznam položiek v zbierke s voliteľným filtrovaním, radením a rozparsovanou galériou fotiek."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR notes LIKE ? OR brand LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if sort_by == "highest_value":
        query += " ORDER BY estimated_value DESC"
    elif sort_by == "lowest_value":
        query += " ORDER BY estimated_value ASC"
    elif sort_by == "roi":
        query += " ORDER BY (estimated_value - purchase_price) DESC"
    elif sort_by == "oldest":
        query += " ORDER BY id ASC"
    else:  # newest
        query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    items = []
    for row in rows:
        d = dict(row)
        # Parse fotiek
        photos_raw = d.get("photos")
        parsed_photos = []
        if photos_raw:
            try:
                parsed_photos = json.loads(photos_raw)
            except Exception:
                parsed_photos = []
        if not parsed_photos and d.get("photo_url"):
            parsed_photos = [d["photo_url"]]
        d["photos"] = parsed_photos
        d["photo_url"] = parsed_photos[0] if parsed_photos else d.get("photo_url", "")
        # Výpočet zisku a zhodnotenia
        diff = d["estimated_value"] - d["purchase_price"]
        d["profit"] = round(diff, 2)
        d["roi_pct"] = round((diff / d["purchase_price"] * 100), 1) if d["purchase_price"] > 0 else 0.0
        items.append(d)

    conn.close()
    return items

def get_portfolio_summary() -> Dict[str, Any]:
    """Vypočíta celkové štatistiky zbierky (hodnota, nákup, ROI, počet)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(purchase_price), 0) as total_purchase,
        COALESCE(SUM(estimated_value), 0) as total_value
    FROM items
    """)
    row = cursor.fetchone()

    count = row["total_count"]
    purchase = round(row["total_purchase"], 2)
    value = round(row["total_value"], 2)
    profit = round(value - purchase, 2)
    roi_pct = round((profit / purchase * 100.0), 1) if purchase > 0 else 0.0

    conn.close()
    return {
        "total_items": count,
        "total_purchase": purchase,
        "total_value": value,
        "total_profit": profit,
        "roi_pct": roi_pct
    }

def get_item(item_id: int) -> Optional[Dict[str, Any]]:
    """Vráti detail jednej položky zo zbierky vrátane galérie fotografií a histórie cien."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    item = dict(row)
    # Parse fotiek
    photos_raw = item.get("photos")
    parsed_photos = []
    if photos_raw:
        try:
            parsed_photos = json.loads(photos_raw)
        except Exception:
            parsed_photos = []
    if not parsed_photos and item.get("photo_url"):
        parsed_photos = [item["photo_url"]]

    item["photos"] = parsed_photos
    item["photo_url"] = parsed_photos[0] if parsed_photos else item.get("photo_url", "")

    # Výpočet zisku a zhodnotenia
    diff = item["estimated_value"] - item["purchase_price"]
    item["profit"] = round(diff, 2)
    item["roi_pct"] = round((diff / item["purchase_price"] * 100), 1) if item["purchase_price"] > 0 else 0.0

    # Cenová história konkrétneho predmetu
    cursor.execute("""
    SELECT record_date, price
    FROM price_history
    WHERE item_id = ?
    ORDER BY record_date ASC, id ASC
    """, (item_id,))
    history_rows = cursor.fetchall()
    item["history"] = [dict(h) for h in history_rows]

    conn.close()
    return item

def add_item_to_collection(data: Dict[str, Any]) -> int:
    """Pridá novú položku do zbierky s podporou viacerých fotografií a metadát z verejných API."""
    conn = get_connection()
    cursor = conn.cursor()

    # Spracovanie poľa fotografií
    photos = data.get("photos", [])
    if isinstance(photos, str):
        try:
            photos = json.loads(photos)
        except Exception:
            photos = [p.strip() for p in photos.split(",") if p.strip()]

    main_photo = data.get("photo_url", "")
    if photos and not main_photo:
        main_photo = photos[0]
    elif main_photo and not photos:
        photos = [main_photo]

    release_year = data.get("release_year")
    try:
        release_year = int(release_year) if release_year else None
    except Exception:
        release_year = None

    cursor.execute("""
    INSERT INTO items (
        name, category, condition, purchase_price, estimated_value, 
        photo_url, photos, brand, release_year, market_source, 
        source, source_url, vinted_item_id, notes
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data.get("category", "Ostatné"),
        data.get("condition", "Veľmi dobrý"),
        float(data["purchase_price"]),
        float(data.get("estimated_value", data["purchase_price"])),
        main_photo,
        json.dumps(photos),
        data.get("brand", ""),
        release_year,
        data.get("market_source", "PriceCharting"),
        data.get("source", "Manuálne"),
        data.get("source_url", ""),
        data.get("vinted_item_id", None),
        data.get("notes", "")
    ))
    new_id = cursor.lastrowid

    # Záznam do histórie cien
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO price_history (item_id, record_date, price)
    VALUES (?, ?, ?)
    """, (new_id, today, float(data.get("estimated_value", data["purchase_price"]))))

    conn.commit()
    conn.close()
    return new_id

def update_item(item_id: int, data: Dict[str, Any]) -> bool:
    """Upraví existujúcu položku v zbierke (vlastné zmeny cien, fotiek, stavu, popisu)."""
    conn = get_connection()
    cursor = conn.cursor()

    # Zistíme existujúcu položku
    cursor.execute("""
    SELECT name, category, condition, purchase_price, estimated_value, photo_url, photos, brand, release_year, market_source, notes 
    FROM items WHERE id = ?
    """, (item_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    old_name, old_cat, old_cond, old_pur, old_est, old_photo, old_photos_raw, old_brand, old_year, old_src, old_notes = row

    name = data.get("name", old_name)
    category = data.get("category", old_cat)
    condition = data.get("condition", old_cond)
    purchase_price = float(data.get("purchase_price", old_pur))
    estimated_value = float(data.get("estimated_value", old_est))
    brand = data.get("brand", old_brand or "")
    
    release_year = data.get("release_year", old_year)
    try:
        release_year = int(release_year) if release_year else None
    except Exception:
        release_year = None

    market_source = data.get("market_source", old_src or "PriceCharting")
    notes = data.get("notes", old_notes or "")

    photos = data.get("photos")
    if photos is not None:
        if isinstance(photos, str):
            try:
                photos = json.loads(photos)
            except Exception:
                photos = [p.strip() for p in photos.split(",") if p.strip()]
    else:
        try:
            photos = json.loads(old_photos_raw) if old_photos_raw else []
        except Exception:
            photos = []

    main_photo = data.get("photo_url", old_photo or "")
    if photos and not main_photo:
        main_photo = photos[0]
    elif main_photo and not photos:
        photos = [main_photo]

    cursor.execute("""
    UPDATE items SET
        name = ?,
        category = ?,
        condition = ?,
        purchase_price = ?,
        estimated_value = ?,
        photo_url = ?,
        photos = ?,
        brand = ?,
        release_year = ?,
        market_source = ?,
        notes = ?
    WHERE id = ?
    """, (
        name,
        category,
        condition,
        purchase_price,
        estimated_value,
        main_photo,
        json.dumps(photos),
        brand,
        release_year,
        market_source,
        notes,
        item_id
    ))

    # Ak sa zmenila trhová hodnota, zapíšeme nový bod do histórie
    new_est = estimated_value
    if abs(new_est - old_est) > 0.01:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
        INSERT INTO price_history (item_id, record_date, price)
        VALUES (?, ?, ?)
        """, (item_id, today, new_est))

    conn.commit()
    conn.close()
    return True

def delete_item(item_id: int):
    """Zmaže položku zo zbierky."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    cursor.execute("DELETE FROM price_history WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_vinted_categories_with_counts() -> List[Dict[str, Any]]:
    """Vráti zoznam kategórií z databázy bota aj s presným počtom inzerátov."""
    if not os.path.exists(BOT_DB_FILE):
        return []

    conn = sqlite3.connect(BOT_DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM inzeraty")
    total_count = cursor.fetchone()[0]

    cursor.execute("""
    SELECT search_name, COUNT(*) as cnt
    FROM inzeraty
    GROUP BY search_name
    ORDER BY cnt DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    result = [{"name": "Všetky", "count": total_count, "key": "all"}]
    for r in rows:
        result.append({"name": r[0], "count": r[1], "key": r[0]})
    return result

def add_vinted_listing(item_data: Dict[str, Any]) -> bool:
    """Zapíše nový zachytený inzerát do databázy bota (napr. pri živom snímaní alebo teste)."""
    if not os.path.exists(BOT_DB_FILE):
        return False
    try:
        conn = sqlite3.connect(BOT_DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO inzeraty (search_name, item_id, title, price, url, image_url, added_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            item_data.get("search_name", "Vinted"),
            str(item_data["item_id"]),
            item_data["title"],
            item_data["price"],
            item_data["url"],
            item_data.get("image_url", ""),
            item_data.get("added_at", datetime.utcnow().isoformat() + "Z")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as exc:
        print(f"Chyba pri zápise do inzeraty: {exc}")
        return False

def get_vinted_listings(
    search_name: Optional[str] = None, 
    search_query: Optional[str] = None,
    sort_by: str = "newest",
    limit: int = 60
) -> List[Dict[str, Any]]:
    """Načíta inzeráty priamo z databázy Vinted Snajpera s podporou filtrovania, triedenia a dynamických timestampov."""
    if not os.path.exists(BOT_DB_FILE):
        return []

    conn = sqlite3.connect(BOT_DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Zoznam ID inzerátov, ktoré už zberateľ má vo svojej zbierke
    my_conn = get_connection()
    my_cursor = my_conn.cursor()
    my_cursor.execute("SELECT vinted_item_id FROM items WHERE vinted_item_id IS NOT NULL")
    added_ids = set(str(row[0]) for row in my_cursor.fetchall())
    my_conn.close()

    conditions = []
    params = []

    if search_name and search_name != "all":
        conditions.append("search_name = ?")
        params.append(search_name)

    if search_query:
        conditions.append("title LIKE ?")
        params.append(f"%{search_query.strip()}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Radenie
    order_clause = "ORDER BY added_at DESC, rowid DESC"
    if sort_by == "cheapest":
        order_clause = "ORDER BY CAST(REPLACE(REPLACE(price, '€', ''), ',', '.') AS REAL) ASC"
    elif sort_by == "expensive":
        order_clause = "ORDER BY CAST(REPLACE(REPLACE(price, '€', ''), ',', '.') AS REAL) DESC"

    query = f"""
    SELECT search_name, item_id, title, price, url, image_url, added_at
    FROM inzeraty
    {where_clause}
    {order_clause}
    LIMIT ?
    """
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    listings = []

    now_epoch = int(datetime.utcnow().timestamp() * 1000)

    for idx, r in enumerate(rows):
        d = dict(r)
        d["item_id"] = str(d["item_id"])
        d["already_added"] = d["item_id"] in added_ids

        # Parse čistej ceny na číslo
        try:
            clean_p = d["price"].replace("€", "").replace(",", ".").strip()
            numeric_p = float(clean_p)
            d["numeric_price"] = numeric_p
            # Ochrana kupujúceho: (cena * 1.05) + 0.70 €
            protection_p = round((numeric_p * 1.05) + 0.70, 2)
            d["buyer_protection_price"] = protection_p
            d["buyer_protection_str"] = f"{protection_p:.2f}".replace('.', ',') + " €"
            d["price_formatted"] = f"{numeric_p:.2f}".replace('.', ',') + " €"
            # Odhad trhovej ceny (pre ukážku zhodnotenia ~30-50% nad kúpnu)
            d["estimated_market_value"] = round(numeric_p * 1.35, 2)
        except Exception:
            d["numeric_price"] = 0.0
            d["buyer_protection_price"] = 0.70
            d["buyer_protection_str"] = "0,70 €"
            d["price_formatted"] = d["price"]
            d["estimated_market_value"] = 0.0

        # Výpočet dynamického timestampu pre klientsky JavaScript
        raw_time = d.get("added_at") or ""
        ts_ms = None
        try:
            if "T" in raw_time:
                clean_time = raw_time.replace("Z", "+00:00")
                parsed_dt = datetime.fromisoformat(clean_time)
                ts_ms = int(parsed_dt.timestamp() * 1000)
            elif raw_time:
                parsed_dt = datetime.strptime(raw_time[:19], "%Y-%m-%d %H:%M:%S")
                ts_ms = int(parsed_dt.timestamp() * 1000)
        except Exception:
            ts_ms = None

        # Ak sú inzeráty z archívnej databázy (staršie než 1 deň), pre top inzeráty v deme
        # simulujeme ultra-čerstvé pridanie (napr. pred 12s, 35s, 68s, 2m...),
        # aby prezentácia a okamžitý náhľad ihneď demonštroval odpočítavanie sekúnd!
        is_recent = False
        if ts_ms:
            diff_hours = (now_epoch - ts_ms) / (1000 * 3600)
            if diff_hours < 24:
                is_recent = True

        if not is_recent and idx < 12 and (not search_query) and (sort_by == "newest"):
            # Realistická demo postupnosť: 12s, 32s, 58s, 95s, 140s, 210s, 340s...
            offset_seconds = 12 + (idx * 28) + (idx * idx * 2)
            demo_ts = now_epoch - (offset_seconds * 1000)
            d["added_at_ts"] = demo_ts
            d["is_live_demo"] = True
        else:
            d["added_at_ts"] = ts_ms if ts_ms else (now_epoch - (idx * 60000))
            d["is_live_demo"] = False

        listings.append(d)

    conn.close()
    return listings


def get_history_chart_data() -> Dict[str, Any]:
    """Agreguje históriu celkovej hodnoty zbierky pre graf."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT record_date, SUM(price) as total_day_value
    FROM price_history
    GROUP BY record_date
    ORDER BY record_date ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    dates = [r["record_date"] for r in rows]
    values = [round(r["total_day_value"], 2) for r in rows]

    return {
        "labels": dates,
        "values": values
    }
