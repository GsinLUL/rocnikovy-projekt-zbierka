"""
notifier.py
===========
Telegram notifikácie pre Vinted Snajper.

Formát správy (HTML):
    <b>Názov produktu</b>
    💰 <b>45,00 €</b> (47,95 €)
    📦 Veľmi dobrý
    🔍 PS2 · 🇵🇱 PL · ⚡ teraz

    [Otvoriť ponuku →]

Všetky hodnoty (krajina, stav, čas) sú DYNAMICKÉ — čítajú sa priamo
z VintedItem objektu naplneného scraperrom, nie sú napísané napevno.
"""

from __future__ import annotations

import json
import logging
import os
import time
import re
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from vinted_scraper import VintedItem

log = logging.getLogger(__name__)

_TG_BASE      = "https://api.telegram.org/bot{token}/{method}"
_CAPTION_LIMIT = 1024


# =============================================================================
# Pomocné funkcie pre caption
# =============================================================================

def _html_escape(text: str) -> str:
    """Escapuje HTML špeciálne znaky pre Telegram HTML parse mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _buyer_protection(price_eur: float) -> float:
    """
    Vypočíta ochranu: (cena * 1.05) + 0.70.
    """
    return round((price_eur * 1.05) + 0.70, 2)


# =============================================================================
# Zostavenie Telegram správy
# =============================================================================

def build_caption(item: "VintedItem", search_name: str) -> str:
    """
    Zostaví caption Telegram správy:
    <b>{Nazov_z_URL}</b>
    💰 {Cena} € ({Cena_s_ochranou} €)
    🔍 {search_name}
    """
    nazov_z_url = _html_escape(item.title)

    if item.price_eur is not None:
        cena_str = f"{item.price_eur:.2f}".replace('.', ',')
        ochrana_str = f"{_buyer_protection(item.price_eur):.2f}".replace('.', ',')
        line_cena = f"💰 {cena_str} € ({ochrana_str} €)"
    elif item.price_str:
        line_cena = f"💰 {_html_escape(item.price_str)}"
    else:
        line_cena = "💰 Info v inzeráte"

    search_safe = _html_escape(search_name)

    caption = (
        f"<b>{nazov_z_url}</b>\n"
        f"{line_cena}\n"
        f"🔍 {search_safe}"
    )
    return caption[:_CAPTION_LIMIT]


def _reply_markup(url: str) -> dict:
    """Inline keyboard s tlačidlom 'Otvoriť ponuku →'."""
    return {
        "inline_keyboard": [
            [{"text": "Otvoriť ponuku →", "url": url}]
        ]
    }


# =============================================================================
# TelegramNotifier
# =============================================================================

class TelegramNotifier:
    """
    Async Telegram notifikátor.
    Posielá sendPhoto (ak item má image_url) s HTML captionom.
    Fallback na sendMessage ak foto zlyhá alebo chýba.
    """

    def __init__(self, token: str, chat_id: str) -> None:
        if not token or not chat_id:
            raise ValueError("TELEGRAM_TOKEN a TELEGRAM_CHAT_ID musia byť v .env")
        self.token   = token
        self.chat_id = chat_id
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        self._client = httpx.AsyncClient(timeout=20.0)

    async def stop(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.stop()

    # ── Verejné API ──────────────────────────────────────────────────────────

    async def send(self, item: "VintedItem", search_name: str = "") -> bool:
        """
        Pošle Telegram správu pre inzerát.
        Vracia True ak bola správa odoslaná úspešne.
        """
        assert self._client, "Notifier nie je spustený"

        caption = build_caption(item, search_name)
        markup  = _reply_markup(item.url)

        # Prednostne sendPhoto, fallback na sendMessage
        if item.image_url:
            ok = await self._send_photo(item.image_url, caption, markup)
            if ok:
                return True
            log.warning("sendPhoto zlyhal → fallback na sendMessage")

        return await self._send_message(caption, markup)

    async def send_startup_message(self) -> None:
        """Startup správa po silent scane."""
        await self._send_message("🤖 <b>Vinted Snajper online a číha na nové úlovky...</b>")

    # ── Interné metódy ────────────────────────────────────────────────────────

    async def _send_photo(self, photo_url: str, caption: str, markup: dict) -> bool:
        api_url = _TG_BASE.format(token=self.token, method="sendPhoto")
        try:
            img = await self._client.get(photo_url, timeout=15.0, follow_redirects=True)
            if img.status_code != 200:
                return False
            files = {"photo": ("photo.jpg", img.content, img.headers.get("content-type", "image/jpeg"))}
            data  = {
                "chat_id":      self.chat_id,
                "caption":      caption,
                "parse_mode":   "HTML",
                "reply_markup": json.dumps(markup),
            }
            resp   = await self._client.post(api_url, data=data, files=files)
            result = resp.json()
            if resp.status_code == 200 and result.get("ok"):
                log.info("Telegram foto OK (id=%s)", result["result"].get("message_id"))
                return True
            log.error("sendPhoto %d: %s", resp.status_code, result.get("description", "?"))
            return False
        except Exception as exc:
            log.error("sendPhoto výnimka: %s", exc)
            return False

    async def _send_message(self, text: str, markup: dict | None = None) -> bool:
        api_url = _TG_BASE.format(token=self.token, method="sendMessage")
        payload: dict = {
            "chat_id":                  self.chat_id,
            "text":                     text,
            "parse_mode":               "HTML",
            "disable_web_page_preview": True,
        }
        if markup:
            payload["reply_markup"] = markup
        try:
            resp   = await self._client.post(api_url, json=payload)
            result = resp.json()
            if resp.status_code == 200 and result.get("ok"):
                log.info("Telegram správa OK (id=%s)", result["result"].get("message_id"))
                return True
            log.error("sendMessage %d: %s", resp.status_code, result.get("description", "?"))
            return False
        except Exception as exc:
            log.error("sendMessage výnimka: %s", exc)
            return False


# =============================================================================
# Factory
# =============================================================================

def notifier_from_env() -> TelegramNotifier:
    token   = os.environ.get("TELEGRAM_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return TelegramNotifier(token=token, chat_id=chat_id)
