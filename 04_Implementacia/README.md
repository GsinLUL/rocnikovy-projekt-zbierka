# 04 · Implementácia – Funkčný zdrojový kód

Tento adresár obsahuje zdrojové kódy softvérového riešenia vyvinutého v súlade s metodikou inšpirovanou RUP.

---

## Štruktúra implementácie

```
04_Implementacia/
├── requirements.txt         # Zoznam závislostí projektu
├── README.md                # Tento prehľadový dokument
└── src/                     # Jadrové zdrojové kódy prototypu
    ├── main.py              # Hlavný demonštračný skript systému
    ├── models.py            # Dátové modely (User, Item, BotFilter, Notification)
    ├── api_service.py       # Modul automatického obohacovania dát cez verejné API
    ├── scraper_bot.py       # Modul autonómneho monitorovacieho skriptu (Vinted Snajper)
    └── notification_engine.py # Interaktívne notifikácie a automatický prepočet hodnoty
```

---

## 1. Jadrový prototyp (`src/`)

Jadrový prototyp v `04_Implementacia/src/` je naprogramovaný v čistom Pythone 3 bez nutnosti inštalovať externé knižnice:
* **Spustenie na macOS / Linux:**
  ```bash
  python3 04_Implementacia/src/main.py
  ```
* **Spustenie na Windows:**
  ```bash
  python 04_Implementacia\src\main.py
  ```

Skript postupne demonštruje:
1. Inicializáciu portfólia a výpočet celkovej hodnoty.
2. Vyhľadanie a automatické doplnenie metadát/fotografií cez API bez manuálneho vypisovania.
3. Spustenie monitorovacieho skriptu na Vintede s definovanými kľúčovými slovami a cenovým stropom.
4. Vygenerovanie interaktívnej notifikácie.
5. **Kľúčovú vlastnosť:** Automatický zápis nájdeného predmetu do databázy a okamžitý prepočet trhovej hodnoty.

---

## 2. Plná webová aplikácia a Vinted Snajper (`aplikacia/`)

Pre potreby reálneho nasadenia a komfortného používania je k dispozícii plnohodnotná webová aplikácia v modernom Apple/Vinted dizajne:
* **Umiestnenie:** `/aplikacia`
* **Technológie:** Python 3 (Flask), SQLite (`zbierka.db`, `vinted_bot.db`), Chart.js, Telegram Bot API.
* **Spustenie:**
  ```bash
  cd aplikacia
  ./run.sh
  ```
  Aplikácia beží na adrese: `http://127.0.0.1:5001`.
