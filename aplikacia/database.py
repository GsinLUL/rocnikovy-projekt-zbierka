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

    # Overenie či existujú východiskové položky
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]

    if count == 0:
        # Pridáme pekné vzorové zberateľské položky
        sample_items = [
            (
                "Sony PlayStation 2 Slim (Čierna, SCPH-70004)",
                "Konzoly",
                "Veľmi dobrý",
                35.00,
                65.00,
                "https://images1.vinted.net/t/05_024b4_8x1hKvdQ1rDps8T1o7BqC3N9/310x430/1715423891.jpeg?s=1",
                "Vinted Snajper",
                "https://www.vinted.sk",
                "sample_ps2",
                "Kúpené s 2 originálnymi DualShock ovládačmi a pamäťovou kartou."
            ),
            (
                "Apple iPod Classic 6th Gen (80GB Silver)",
                "Retro elektronika",
                "Výborný",
                45.00,
                110.00,
                "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
                "Vinted Snajper",
                "https://www.vinted.sk",
                "sample_ipod",
                "Nová batéria, originálny predný kryt bez škrabancov."
            ),
            (
                "Nintendo Game Boy Color (Atomic Purple)",
                "Konzoly",
                "Dobrý",
                50.00,
                95.00,
                "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?w=600&auto=format&fit=crop&q=80",
                "Manuálne",
                "",
                None,
                "Originálny priehľadný fialový kryt."
            ),
            (
                "Sony Cyber-shot DSC-W80 Retro Digitál",
                "Fotoaparáty",
                "Veľmi dobrý",
                20.00,
                55.00,
                "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
                "Vinted Snajper",
                "https://www.vinted.sk",
                "sample_sony",
                "Funkčná batéria aj nabíjačka, retro estetika 2000s."
            )
        ]

        cursor.executemany("""
        INSERT INTO items (name, category, condition, purchase_price, estimated_value, photo_url, source, source_url, vinted_item_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_items)

        # Doplníme fiktívnu cenovú históriu pre graf
        cursor.execute("SELECT id, estimated_value FROM items")
        for row in cursor.fetchall():
            item_id = row[0]
            val = row[1]
            history = [
                (item_id, "2026-06-01", round(val * 0.82, 2)),
                (item_id, "2026-07-15", round(val * 0.88, 2)),
                (item_id, "2026-08-30", round(val * 0.94, 2)),
                (item_id, "2026-10-15", val)
            ]
            cursor.executemany("INSERT INTO price_history (item_id, record_date, price) VALUES (?, ?, ?)", history)

    conn.commit()
    conn.close()

def get_all_items(search_query: str = "", category: str = "", sort_by: str = "newest") -> List[Dict[str, Any]]:
    """Vráti zoznam položiek v zbierke s voliteľným filtrovaním a radením."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR notes LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

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
    items = [dict(row) for row in rows]
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

def add_item_to_collection(data: Dict[str, Any]) -> int:
    """Pridá novú položku do zbierky a zaznamená počiatočnú cenovú históriu."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO items (name, category, condition, purchase_price, estimated_value, photo_url, source, source_url, vinted_item_id, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data.get("category", "Ostatné"),
        data.get("condition", "Veľmi dobrý"),
        float(data["purchase_price"]),
        float(data.get("estimated_value", data["purchase_price"])),
        data.get("photo_url", ""),
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

def delete_item(item_id: int):
    """Zmaže položku zo zbierky."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    cursor.execute("DELETE FROM price_history WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_vinted_listings(search_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Načíta inzeráty priamo z databázy Vinted Snajpera."""
    if not os.path.exists(BOT_DB_FILE):
        return []

    conn = sqlite3.connect(BOT_DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Zoznam ID inzerátov, ktoré už zberateľ má vo svojej zbierke
    my_conn = get_connection()
    my_cursor = my_conn.cursor()
    my_cursor.execute("SELECT vinted_item_id FROM items WHERE vinted_item_id IS NOT NULL")
    added_ids = set(row[0] for row in my_cursor.fetchall())
    my_conn.close()

    if search_name and search_name != "all":
        cursor.execute("""
        SELECT search_name, item_id, title, price, url, image_url, added_at
        FROM inzeraty
        WHERE search_name = ?
        ORDER BY added_at DESC
        LIMIT ?
        """, (search_name, limit))
    else:
        cursor.execute("""
        SELECT search_name, item_id, title, price, url, image_url, added_at
        FROM inzeraty
        ORDER BY added_at DESC
        LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    listings = []
    for r in rows:
        d = dict(r)
        d["already_added"] = d["item_id"] in added_ids
        # Parse čistej ceny na číslo
        try:
            clean_p = d["price"].replace("€", "").replace(",", ".").strip()
            d["numeric_price"] = float(clean_p)
            # Odhad trhovej ceny (pre ukážku zhodnotenia ~30-50% nad kúpnu)
            d["estimated_market_value"] = round(d["numeric_price"] * 1.35, 2)
        except Exception:
            d["numeric_price"] = 0.0
            d["estimated_market_value"] = 0.0
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
