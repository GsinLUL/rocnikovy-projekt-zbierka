"""
database.py
===========
SQLite vrstva pre Vinted Snajper.

Zodpovednosti:
- Spravovať tabuľku inzeraty s composite PK (search_name, item_id)
- Každé hľadanie má vlastnú sadu záznamov — rovnaké ID v rôznych hľadaniach
  sú nezávislé
- Po každom scane automaticky orezať staré záznamy na max. 100 najnovších
  na jedno hľadanie (trim_to_limit)
- Migroval starú schému (seen_items) na novú (inzeraty) bez straty dát
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

_DEFAULT_DB_PATH = "vinted_bot.db"
_MAX_RECORDS_PER_SEARCH = 100

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SQL definície
# ─────────────────────────────────────────────────────────────────────────────

# Hlavná tabuľka. Vždy sa vytvára pri štarte (CREATE TABLE IF NOT EXISTS).
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS inzeraty (
    search_name TEXT NOT NULL,
    item_id     TEXT NOT NULL,
    title       TEXT NOT NULL DEFAULT '',
    price       TEXT         DEFAULT '',
    url         TEXT         DEFAULT '',
    image_url   TEXT         DEFAULT '',
    added_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (search_name, item_id)
);
"""

# SQLite indexuje rowid automaticky — nie je potrebný explicitný index.
# Pre trim_to_limit (ORDER BY rowid DESC) to bude vždy efektívne.

_INSERT_ITEM = """
INSERT OR IGNORE INTO inzeraty
    (search_name, item_id, title, price, url, image_url, added_at)
VALUES
    (?, ?, ?, ?, ?, ?, ?);
"""

_EXISTS_ITEM = """
SELECT 1 FROM inzeraty
WHERE search_name = ? AND item_id = ?
LIMIT 1;
"""

_COUNT_FOR_SEARCH = """
SELECT COUNT(*) FROM inzeraty WHERE search_name = ?;
"""

# Vymaž všetky záznamy okrem najnovších 100 pre dané hľadanie.
# LIMIT -1 OFFSET 100 je platná SQLite syntax: vyberie všetky riadky od pozície 100.
_TRIM_OLD = """
DELETE FROM inzeraty WHERE rowid IN (
    SELECT rowid FROM inzeraty
    WHERE search_name = ?
    ORDER BY added_at DESC
    LIMIT -1 OFFSET 100
)
"""


# ─────────────────────────────────────────────────────────────────────────────
# Migrácia — stará schéma → nová
# ─────────────────────────────────────────────────────────────────────────────

def _migrate(conn: sqlite3.Connection) -> None:
    """
    Ak existuje stará tabuľka seen_items, prenesie záznamy do inzeraty
    a tabuľku seen_items odstráni.
    """
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='seen_items';"
    )
    if cur.fetchone() is None:
        return  # Stará tabuľka neexistuje, nič netreba migrovať

    logger.info("🔄 DB Migrácia: seen_items → inzeraty...")

    # Vytvoríme cieľovú tabuľku ak ešte neexistuje
    conn.execute(_CREATE_TABLE)

    # Prenesieme záznamy; first_seen → added_at, search_name='legacy' ak chýba
    conn.execute("""
        INSERT OR IGNORE INTO inzeraty
            (search_name, item_id, title, price, url, image_url, added_at)
        SELECT
            COALESCE(search_name, 'legacy'),
            item_id,
            COALESCE(title, ''),
            COALESCE(price, ''),
            COALESCE(url, ''),
            COALESCE(image_url, ''),
            COALESCE(first_seen, datetime('now'))
        FROM seen_items;
    """)

    count = conn.execute("SELECT COUNT(*) FROM inzeraty;").fetchone()[0]
    conn.execute("DROP TABLE seen_items;")
    conn.commit()
    logger.info("✅ Migrácia dokončená: %d záznamov prenesených do 'inzeraty'.", count)


# ─────────────────────────────────────────────────────────────────────────────
# Trieda Database
# ─────────────────────────────────────────────────────────────────────────────

class Database:
    """
    Synchronná SQLite obálka (volá sa z async kódu cez asyncio.to_thread).

    Každé hľadanie (search_name) má vlastný priestor v DB.
    Limit: max 100 najnovších záznamov na jedno hľadanie.
    """

    def __init__(self, path: str = _DEFAULT_DB_PATH) -> None:
        self.path = Path(path)
        self._conn: sqlite3.Connection | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Otvoriť spojenie, spustiť migráciu a vytvoriť schému ak neexistuje."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")

        # Migrácia pred vytvorením novej schémy
        _migrate(self._conn)

        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()
        logger.info("DB pripojená: %s", self.path)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_):
        self.close()

    # ── Verejné metódy ────────────────────────────────────────────────────────

    def is_seen(self, search_name: str, item_id: str) -> bool:
        """
        Vráti True, ak (search_name, item_id) už existuje v DB.
        Každé hľadanie má vlastný priestor — rovnaké ID v rôznych hľadaniach
        sú nezávislé.
        """
        assert self._conn, "Databáza nie je otvorená."
        row = self._conn.execute(_EXISTS_ITEM, (search_name, item_id)).fetchone()
        return row is not None

    def mark_seen(
        self,
        search_name: str,
        item_id: str,
        title: str = "",
        price: str = "",
        url: str = "",
        image_url: str = "",
    ) -> bool:
        """
        Uloží inzerát pod daným hľadaním.
        Vracia True ak bol pridaný (nový), False ak už existoval.
        """
        assert self._conn, "Databáza nie je otvorená."
        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        cursor = self._conn.execute(
            _INSERT_ITEM,
            (search_name, item_id, title, price, url, image_url or "", now),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def trim_to_limit(
        self,
        search_name: str,
        limit: int = _MAX_RECORDS_PER_SEARCH,
    ) -> int:
        """
        Orezá záznamy pre `search_name` na `limit` najnovších (podľa ROWID).
        Vracia počet vymazaných záznamov.
        Loguje ak prebehlo čistenie.
        """
        assert self._conn, "Databáza nie je otvorená."

        count = self._conn.execute(
            _COUNT_FOR_SEARCH, (search_name,)
        ).fetchone()[0]

        if count <= limit:
            return 0  # Nič na čistenie

        try:
            cursor = self._conn.execute(_TRIM_OLD, (search_name,))
            deleted = cursor.rowcount
            self._conn.commit()
        except sqlite3.OperationalError as e:
            # Fallback for the case where table `inzeraty` does not exist
            # because the database has `seen_items` instead.
            logger.error(f"SQL Error in trim_to_limit: {e}")
            return 0

        if deleted > 0:
            logger.info(
                "🧹 Údržba: Pre [%s] držím v pamäti %d najnovších ID. (vymazaných: %d)",
                search_name, limit, deleted,
            )

        return deleted

    def count_for_search(self, search_name: str) -> int:
        """Počet uložených záznamov pre dané hľadanie."""
        assert self._conn, "Databáza nie je otvorená."
        row = self._conn.execute(_COUNT_FOR_SEARCH, (search_name,)).fetchone()
        return row[0] if row else 0

    def total_seen(self) -> int:
        """Celkový počet uložených záznamov vo všetkých hľadaniach."""
        assert self._conn, "Databáza nie je otvorená."
        row = self._conn.execute("SELECT COUNT(*) FROM inzeraty;").fetchone()
        return row[0] if row else 0
