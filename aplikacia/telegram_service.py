"""
telegram_service.py - Telegram notifikačná služba pre Zbierku & Vinted Snajper
Posiela interaktívne notifikácie do Telegram chatu s fotografiou, cenou s ochranou kupujúceho,
odkazom priamo na inzerát a tlačidlom 'Otvoriť ponuku →'.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import httpx

log = logging.getLogger("telegram_service")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "bot", "config.json")
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
BOT_ENV_PATH = os.path.join(os.path.dirname(__file__), "bot", ".env")

def _load_env_file(path: str) -> Dict[str, str]:
    env = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
    return env

def get_telegram_credentials() -> Dict[str, str]:
    """Zistí token a chat ID z prostredia, .env súborov alebo config.json."""
    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    # Kontrola .env
    for ep in [ENV_PATH, BOT_ENV_PATH]:
        if not token or not chat_id:
            env_vars = _load_env_file(ep)
            if not token:
                token = env_vars.get("TELEGRAM_TOKEN", "")
            if not chat_id:
                chat_id = env_vars.get("TELEGRAM_CHAT_ID", "")

    # Kontrola config.json
    if not token or not chat_id:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    settings = cfg.get("settings", {})
                    if not token:
                        token = settings.get("telegram_token", "")
                    if not chat_id:
                        chat_id = str(settings.get("telegram_chat_id", ""))
            except Exception:
                pass

    return {
        "token": token,
        "chat_id": chat_id,
        "is_configured": bool(token and chat_id)
    }

def save_telegram_credentials(token: str, chat_id: str) -> bool:
    """Uloží Telegram prihlasovacie údaje do config.json a .env."""
    token = token.strip()
    chat_id = chat_id.strip()

    # 1. Zápis do config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {"settings": {}, "searches": []}
    else:
        cfg = {"settings": {}, "searches": []}

    cfg.setdefault("settings", {})
    cfg["settings"]["telegram_token"] = token
    cfg["settings"]["telegram_chat_id"] = chat_id

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as exc:
        log.error(f"Chyba zápisu config.json: {exc}")
        return False

    # 2. Zápis do .env
    try:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"TELEGRAM_TOKEN={token}\n")
            f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
    except Exception:
        pass

    return True

def calculate_buyer_protection(price_eur: float) -> float:
    """Vinted vzorec pre ochranu kupujúceho: (cena * 1.05) + 0.70 €."""
    return round((price_eur * 1.05) + 0.70, 2)

def send_telegram_notification(
    title: str,
    price_eur: float,
    url: str,
    image_url: Optional[str] = None,
    search_name: str = "Vinted Snajper",
    custom_badge: Optional[str] = None
) -> Dict[str, Any]:
    """
    Odošle Telegram notifikáciu zhodnú s botom Vinted Snajper.
    Formát:
        <b>{Názov}</b>
        💰 {Cena} € ({Cena s ochranou} €)
        🔍 {Kategória} · ⚡ {čas}
        [Otvoriť ponuku →]
    """
    creds = get_telegram_credentials()
    if not creds["is_configured"]:
        return {
            "success": False,
            "error": "Telegram nie je nakonfigurovaný (chýba TELEGRAM_TOKEN alebo TELEGRAM_CHAT_ID). Nastavte ich v nastaveniach.",
            "simulated": True
        }

    token = creds["token"]
    chat_id = creds["chat_id"]

    # Výpočet ochrany kupujúceho
    protection_eur = calculate_buyer_protection(price_eur)
    cena_str = f"{price_eur:.2f}".replace('.', ',')
    ochrana_str = f"{protection_eur:.2f}".replace('.', ',')

    badge = custom_badge or "⚡ práve teraz"
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_search = search_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    caption = (
        f"<b>{safe_title}</b>\n"
        f"💰 <b>{cena_str} €</b> ({ochrana_str} € s ochranou)\n"
        f"🔍 {safe_search} · {badge}"
    )

    markup = {
        "inline_keyboard": [
            [{"text": "Otvoriť ponuku →", "url": url}]
        ]
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            # 1. Pokus poslať s fotografiou
            if image_url:
                try:
                    img_resp = client.get(image_url, follow_redirects=True, timeout=8.0)
                    if img_resp.status_code == 200:
                        api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        files = {"photo": ("item.jpg", img_resp.content, "image/jpeg")}
                        data = {
                            "chat_id": chat_id,
                            "caption": caption[:1024],
                            "parse_mode": "HTML",
                            "reply_markup": json.dumps(markup)
                        }
                        resp = client.post(api_url, data=data, files=files)
                        res_json = resp.json()
                        if resp.status_code == 200 and res_json.get("ok"):
                            return {"success": True, "message_id": res_json["result"]["message_id"]}
                except Exception as img_err:
                    log.warning(f"sendPhoto zlyhal ({img_err}), skúšam fallback na textovú správu")

            # 2. Textový fallback
            api_url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": caption[:4096],
                "parse_mode": "HTML",
                "reply_markup": markup,
                "disable_web_page_preview": False
            }
            resp = client.post(api_url, json=payload)
            res_json = resp.json()
            if resp.status_code == 200 and res_json.get("ok"):
                return {"success": True, "message_id": res_json["result"]["message_id"]}
            else:
                return {
                    "success": False,
                    "error": res_json.get("description", f"Chyba Telegram API (kód {resp.status_code})")
                }

    except Exception as exc:
        log.error(f"Výnimka pri odosielaní do Telegramu: {exc}")
        return {"success": False, "error": str(exc)}
