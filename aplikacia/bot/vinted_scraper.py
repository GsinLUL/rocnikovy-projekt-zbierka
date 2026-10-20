"""
vinted_scraper.py  —  Vinted Snajper
================================
Agresívny multi-search scraper pre Vinted.sk.
Všetky nastavenia sa načítavajú z config.json.

Spustenie:
    python vinted_scraper.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import Stealth

from database import Database
from notifier import notifier_from_env

load_dotenv()

# =============================================================================
# Konfigurácia — načítava sa z config.json
# =============================================================================

_CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """Načíta config.json. Podporuje štruktúru so 'settings' objektom."""
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(f"config.json sa nenašiel: {_CONFIG_PATH}")
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    if "settings" in raw:
        settings = raw["settings"]
        cfg: dict = {
            "db_path":      settings.get("db_path", "vinted_bot.db"),
            "interval_min": settings.get("check_interval_min", 20),
            "interval_max": settings.get("check_interval_max", 40),
            "item_limit":   settings.get("item_limit", 10),
            "searches":     raw.get("searches", []),
        }
    else:
        cfg = raw
        cfg.setdefault("db_path", "vinted_bot.db")
        cfg.setdefault("interval_min", 20)
        cfg.setdefault("interval_max", 40)
        cfg.setdefault("item_limit", 10)

    if "searches" not in cfg or not cfg["searches"]:
        raise ValueError("config.json musí obsahovať neprázdny zoznam 'searches'")
    for s in cfg["searches"]:
        if "url" not in s:
            raise ValueError(f"Každé hľadanie musí mať 'url'. Chybný záznam: {s}")
        s.setdefault("name", "Vinted")
        s.setdefault("keywords", [])
        s.setdefault("max_price", None)

    return cfg


# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# =============================================================================
# Stav bota — zapisuje sa do bot_status.json
# =============================================================================

_STATUS_PATH = Path(__file__).parent / "bot_status.json"


def update_bot_status(
    status: str,
    current_task: Optional[str] = None,
    next_run_in: Optional[float] = None,
) -> None:
    """
    Zapíše aktuálny stav bota do bot_status.json.

    Args:
        status:       'Searching' | 'Sleeping' | 'Starting' | 'Stopped' | 'Error'
        current_task: Názov úlohy (napr. meno hľadania)
        next_run_in:  Počet sekúnd do ďalšieho spustenia (pri Sleeping)
    """
    payload: dict = {
        "status": status,
        "current_task": current_task,
        "next_run_in": next_run_in,
        "next_run_at": (
            time.time() + next_run_in if next_run_in is not None else None
        ),
        "updated_at": time.time(),
    }
    try:
        with open(_STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception as exc:
        log.warning("Nemožno zapísať bot_status.json: %s", exc)


# =============================================================================
# Výnimky
# =============================================================================

class VintedBlockedError(Exception):
    def __init__(self, status: int, url: str = "") -> None:
        self.status = status
        super().__init__(f"HTTP {status} pri '{url}' — bot je pravdepodobne blokovaný")


class _NullAsyncCtx:
    async def __aenter__(self): return None
    async def __aexit__(self, *_): pass


# =============================================================================
# Dátový model
# =============================================================================

@dataclass
class VintedItem:
    item_id:   str
    title:     str
    price_str: str
    price_eur: Optional[float]
    url:       str
    image_url: Optional[str] = None
    skipped_reason: str = ""

    @property
    def is_accepted(self) -> bool:
        return not self.skipped_reason


# =============================================================================
# Konštanty pre extrakciu
# =============================================================================

# Selektory pre nájdenie boxov s inzerátmi
_ITEM_BOX_SEL = "div[data-testid^='grid-item']"
_ITEM_BOX_FALLBACKS = [
    ".new-item-box",
    "[data-testid='item-box']",
    "div[class*='feed-grid__item']",
    "article[class*='item']",
]

# Selektory pre link v boxe
_LINK_SELECTORS = [
    "a[data-testid$='item-link']",
    "a.new-item-box__overlay",
    "a[class*='new-item-box__overlay']",
    "a",
]

# Selektory pre obrázok
_IMG_SELECTORS = ["img[src]", "img[data-src]"]

# Regex pre cenu: hľadá vzory ako '45,00 €' alebo '45 €'
_PRICE_RE = re.compile(r"(\d{1,5}[,.]\d{2})\s*€|(\d{1,5})\s*€")

# Regex pre extrakciu číselnej hodnoty z price_str
_NUM_RE = re.compile(r"(\d[\d\s]*[,.]?\d*)")

# Realistické User-Agents
_USER_AGENTS = [
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
]


# =============================================================================
# Parsovanie URL
# =============================================================================

_ID_RE   = re.compile(r"/(\d{6,})")
_SLUG_RE = re.compile(r"/(?:\d{6,})-([^/?#]+)")


def extract_item_id(url: str) -> str:
    m = _ID_RE.search(url)
    return m.group(1) if m else url


def title_from_url(url: str) -> str:
    """Vytiahne slug z URL → čitateľný názov. Pr.: sony-ps2-slim → 'Sony Ps2 Slim'"""
    m = _SLUG_RE.search(url)
    if not m:
        return ""
    return re.sub(r"[-_]+", " ", m.group(1)).strip().title()


def parse_price_eur(price_str: str) -> Optional[float]:
    """Prevedie '45,00 €' alebo '45 €' na float 45.0"""
    cleaned = price_str.replace("\xa0", " ").strip()
    m = _NUM_RE.search(cleaned)
    if not m:
        return None
    try:
        return float(m.group(1).replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


# =============================================================================
# Pomocné funkcie — Browser
# =============================================================================

async def _quick_pause(min_s: float = 0.8, max_s: float = 1.5) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


async def dismiss_cookie_banner(page: Page) -> None:
    for sel in [
        "button[data-testid='onetrust-accept-btn-handler']",
        "button#onetrust-accept-btn-handler",
        "button >> text=Accept all",
    ]:
        try:
            btn = page.locator(sel).first
            if await btn.is_visible(timeout=1500):
                await btn.click()
                await asyncio.sleep(0.4)
                return
        except Exception:
            continue


async def _safe_attr(el, selector: str, attr: str) -> str:
    try:
        node = await el.query_selector(selector)
        if node is None:
            return ""
        val = await node.get_attribute(attr)
        return (val or "").strip()
    except Exception:
        return ""


# =============================================================================
# HLAVNÁ EXTRAKCIA — každý box inzerátu
# =============================================================================

async def _scrape_listing_page(page: Page, item_limit: int) -> list[dict]:
    """
    Skenuje stránku a vracia základné dáta (URL, cena, foto) pre každý inzerát.
    """
    raw: list[dict] = []

    # ── Nájdi boxy ──────────────────────────────────────────────────────────
    boxes = await page.query_selector_all(_ITEM_BOX_SEL)
    if not boxes:
        for sel in _ITEM_BOX_FALLBACKS:
            boxes = await page.query_selector_all(sel)
            if boxes:
                break

    if not boxes:
        log.warning("Žiadne item-boxy na stránke — pravdepodobne blokovaní alebo zlý selektor")
        return raw

    for box in boxes[:item_limit]:
        entry = {}

        # 1. URL inzerátu
        item_url = ""
        for lsel in _LINK_SELECTORS:
            href = await _safe_attr(box, lsel, "href")
            if href:
                item_url = href if href.startswith("http") else f"https://www.vinted.sk{href}"
                break
        if not item_url:
            continue
        entry["url"] = item_url

        # 2. Cena z textu boxu pomocou regexu (\d+,\d+)\s*€
        try:
            raw_text = await box.inner_text()
        except Exception:
            raw_text = ""

        m = re.search(r"(\d+,\d+)\s*€", raw_text)
        if m:
            entry["price_str"] = f"{m.group(1)} €"
        else:
            entry["price_str"] = ""

        # 3. URL obrázka
        for img_attr in ("src", "data-src"):
            src = await _safe_attr(box, "img", img_attr)
            if src and not src.startswith("data:"):
                entry["image_url"] = src
                break

        raw.append(entry)

    return raw


# =============================================================================
# Filtrovacia logika
# =============================================================================

def apply_search_filter(item: VintedItem, search_cfg: dict) -> None:
    """Aplikuje cenový a keyword filter z konfigurácie."""
    keywords: list[str] = search_cfg.get("keywords", [])
    max_price: Optional[float] = search_cfg.get("max_price")

    # Cenový filter
    if max_price is not None and item.price_eur is not None:
        if item.price_eur > max_price:
            item.skipped_reason = f"cena {item.price_eur:.2f} € > limit {max_price:.2f} €"
            return

    # Keyword filter — prázdny zoznam = posiela všetko
    if not keywords:
        return

    combined = normalise(item.title)
    for kw in keywords:
        if normalise(kw) in combined:
            return

    item.skipped_reason = "nezodpovedá žiadnemu kľúčovému slovu"


# =============================================================================
# Hlavná scraping funkcia pre jedno hľadanie
# =============================================================================

async def get_new_items(
    context: BrowserContext,
    db: Database,
    search_cfg: dict,
    item_limit: int,
) -> list[VintedItem]:
    """Naskenuje jedno hľadanie a vráti nové inzeráty (nevidené, prešlé filtrami)."""
    url         = search_cfg["url"]
    search_name = search_cfg.get("name", "Vinted")

    page    = await context.new_page()
    results: list[VintedItem] = []

    try:
        log.info("[%s] ➜ %s", search_name, url)
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=45_000)

        if resp is not None and resp.status in (403, 429, 503):
            raise VintedBlockedError(resp.status, url)

        await _quick_pause(0.8, 1.5)
        await dismiss_cookie_banner(page)

        raw_entries = await _scrape_listing_page(page, item_limit)

    finally:
        await page.close()

    skipped_dup = skipped_filter = accepted = 0

    for entry in raw_entries:
        item_url = entry.get("url", "")
        if not item_url:
            continue

        item_id = extract_item_id(item_url)

        # Názov primárne zo slug-u URL — 100% spoľahlivé
        title = title_from_url(item_url) or "(bez názvu)"

        # Cena — raw string a float hodnota
        price_str: str          = entry.get("price_str", "")
        price_eur: Optional[float] = parse_price_eur(price_str)

        # Deduplikácia — per search_name (rovnaké ID v rôznych hľadaniach sú nezávislé)
        if await asyncio.to_thread(db.is_seen, search_name, item_id):
            skipped_dup += 1
            continue

        item = VintedItem(
            item_id   = item_id,
            title     = title,
            price_str = price_str,
            price_eur = price_eur,
            url       = item_url,
            image_url = entry.get("image_url"),
        )

        # Filtre
        apply_search_filter(item, search_cfg)

        if item.skipped_reason:
            skipped_filter += 1
            # Ulož aj odfiltrované — aby sme ich pri ďalšom scane preskočili
            await asyncio.to_thread(
                db.mark_seen, search_name, item_id, title, price_str, item_url, ""
            )
            continue

        log.info(
            "🆕 [%s] %s | %s",
            search_name, title, price_str or "Info v inzeráte"
        )
        accepted += 1
        results.append(item)

    log.info(
        "[%s] ✔ %d nových | %d duplikátov | %d odfiltrovaných",
        search_name, accepted, skipped_dup, skipped_filter,
    )

    return results


# =============================================================================
# Browser context
# =============================================================================

async def _make_context(browser):
    context = await browser.new_context(
        user_agent=random.choice(_USER_AGENTS),
        locale="sk-SK",
        timezone_id="Europe/Bratislava",
        viewport={"width": 1366, "height": 768},
        extra_http_headers={
            "Accept-Language": "sk-SK,sk;q=0.9,cs;q=0.8,en;q=0.7",
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "DNT": "1",
        },
    )
    stealth = Stealth(
        navigator_languages_override=("sk-SK", "sk"),
        navigator_platform_override="MacIntel",
    )
    await stealth.apply_stealth_async(context)
    return context


# =============================================================================
# Hlavná slučka
# =============================================================================

_BLOCKED_WAIT = 300   # 5 minút po 403/429
_ERROR_WAIT   = 45


async def main_loop() -> None:
    cfg          = load_config()
    searches     = cfg["searches"]
    item_limit   = cfg["item_limit"]
    interval_min = cfg["interval_min"]
    interval_max = cfg["interval_max"]
    db_path      = cfg["db_path"]

    log.info("=" * 60)
    log.info("  🎯 VINTED SNAJPER ŠTARTUJE  |  %d hľadaní  |  interval %g–%g s",
             len(searches), interval_min, interval_max)
    for s in searches:
        mp = f"{s['max_price']} €" if s.get("max_price") else "bez limitu"
        log.info("  → %-15s  max_price: %s", s["name"], mp)
    log.info("=" * 60)

    update_bot_status("Starting", current_task="Inicializácia")

    try:
        notifier = notifier_from_env()
    except ValueError as exc:
        log.warning("Telegram nenakonfigurovaný (%s) — notifikácie vypnuté", exc)
        notifier = None

    with Database(db_path) as db:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )

            async with (notifier if notifier else _NullAsyncCtx()) as active_notifier:

                iteration = 0
                while True:
                    iteration += 1
                    is_silent = (iteration == 1)

                    if is_silent:
                        log.info("━━━ SILENT START — mapujem existujúce inzeráty ━━━")
                    else:
                        log.info("━━━ Iterácia #%d ━━━", iteration)

                    context = None
                    try:
                        context = await _make_context(browser)

                        for search_cfg in searches:
                            search_name = search_cfg.get("name", "Vinted")
                            update_bot_status("Searching", current_task=search_name)
                            try:
                                new_items = await get_new_items(
                                    context, db, search_cfg, item_limit
                                )
                            except VintedBlockedError as exc:
                                log.error("[%s] BLOKOVANÝ: %s", search_name, exc)
                                update_bot_status("Sleeping", current_task=f"Blokovaný — čakám {_BLOCKED_WAIT}s", next_run_in=_BLOCKED_WAIT)
                                await asyncio.sleep(_BLOCKED_WAIT)
                                continue
                            except Exception as exc:
                                log.error("[%s] Chyba: %s", search_name, exc, exc_info=True)
                                update_bot_status("Error", current_task=search_name)
                                continue

                            if is_silent:
                                # Silent start — uložiť do DB, neposielať na Telegram
                                for item in new_items:
                                    await asyncio.to_thread(
                                        db.mark_seen,
                                        search_name, item.item_id, item.title,
                                        item.price_str, item.url, item.image_url or "",
                                    )
                            else:
                                # Normálny beh — posielaj nové okamžite
                                for item in new_items:
                                    if active_notifier:
                                        sent = await active_notifier.send(item, search_name)
                                        if sent:
                                            await asyncio.to_thread(
                                                db.mark_seen,
                                                search_name, item.item_id, item.title,
                                                item.price_str, item.url, item.image_url or "",
                                            )
                                            log.info("✓ Telegram: %s", item.title)
                                        else:
                                            log.warning("✗ Telegram zlyhal: %s", item.title)
                                    else:
                                        await asyncio.to_thread(
                                            db.mark_seen,
                                            search_name, item.item_id, item.title,
                                            item.price_str, item.url, item.image_url or "",
                                        )

                            # Po každom scane orez DB na 100 najnovších pre toto hľadanie
                            await asyncio.to_thread(db.trim_to_limit, search_name)

                        if is_silent:
                            log.info("Silent Start dokončený.")
                            if active_notifier:
                                await active_notifier.send_startup_message()

                        wait = random.uniform(interval_min, interval_max)
                        log.info("🔭 Ďalšia kontrola o %.0f s...", wait)
                        update_bot_status("Sleeping", current_task=None, next_run_in=wait)
                        await asyncio.sleep(wait)

                    except Exception as exc:
                        log.error("Neočakávaná chyba: %s", exc, exc_info=True)
                        update_bot_status("Error", current_task="Neočakávaná chyba", next_run_in=_ERROR_WAIT)
                        await asyncio.sleep(_ERROR_WAIT)

                    finally:
                        if context:
                            await context.close()

            await browser.close()

    update_bot_status("Stopped")


if __name__ == "__main__":
    asyncio.run(main_loop())
