# Aplikácia Zbierka & Vinted Snajper

Tento podriečinok obsahuje **kompletnú, plnohodnotnú aplikáciu pre zberateľov** s moderným Apple/Vinted rozhraním a integrovaným autonómnym botom.

---

## 🚀 Rýchle spustenie aplikácie

Stačí spustiť skript:
```bash
./run.sh
```
alebo:
```bash
python3 app.py
```

Aplikácia sa automaticky spustí a otvorí webový portál na:  
👉 **http://127.0.0.1:5001**

---

## 🌟 Kľúčové funkcie a rozhranie

1. **📦 Moja zbierka (Portfólio):**
   - Prehľadné karty zberateľských predmetov s fotografiami a cenami.
   - Súhrnné Apple karty: Celková hodnota zbierky, celkový investovaný kapitál, čistý zisk (ROI) v percentách a počet položiek.
   - Rýchle vyhľadávanie a filtrovanie podľa kategórií (Konzoly, Retro elektronika, Fotoaparáty, LEGO, atď.).

2. **✨ Automatické dopĺňanie metadát a fotografií cez API:**
   - Kliknite na tlačidlo **„+ Pridať s API“**.
   - Stačí začať písať názov položky (napr. *PS2*, *iPod*, *Nintendo Switch*, *Charizard*, *Sony kamera*).
   - Systém okamžite z verejného katalógu **automaticky doplní oficiálny názov, kategóriu, rok vydania, stav, referenčnú fotografiu aj odhadovanú trhovú hodnotu**.
   - Používateľ nemusí manuálne nič zdĺhavo vypisovať!

3. **⚡ Vinted Snajper (Živý feed a jedno-klikové pridávanie):**
   - Priame prepojenie s databázou bota (`bot/vinted_bot.db`).
   - Zobrazuje najnovšie inzeráty z Vintedu s fotografiami, cenami a odkazmi.
   - **KĽÚČOVÁ VLASTNOSŤ:** Tlačidlo **„★ Pridať“** na každej karte inzerátu. Po kliknutí sa inzerát ihneď zapíše do zberateľskej databázy, hodnota zbierky sa okamžite prepočíta a zobrazí sa Apple-style notifikácia.

4. **📈 Cenové trendy & Analytika:**
   - Interaktívny graf (Chart.js) vývoja trhovej hodnoty vašej zbierky v čase.

5. **🤖 Správa bota:**
   - Prehľad sledovaných hľadaní (PS2, iPod, Nintendo, Xbox, Playstation, ps3, sony kamera).
   - Možnosť pridať nové kľúčové slovo pre bota priamo cez webové rozhranie.

---

## 📁 Štruktúra podriečinka `aplikacia/`

- `app.py` – hlavný Flask server prepájajúci portfólio s botom
- `database.py` – správa SQLite databázy zbierky (`zbierka.db`) a čítanie inzerátov z bota
- `api_catalog.py` – verejná katalógová služba pre automatické dopĺňanie dát a fotografií
- `templates/index.html` – moderné, responzívne používateľské rozhranie (Apple minimalizmus + Vinted dizajn)
- `static/css/style.css` – čistý dizajn, Apple typography (SF Pro), karty a animácie
- `static/js/app.js` – logika jedno-klikového pridávania, autocomplete a grafy
- `bot/` – originálne súbory bota Vinted Snajper (`vinted_scraper.py`, `notifier.py`, `database.py`, `dashboard.py`, `config.json`, `vinted_bot.db`)
- `run.sh` – jednoduchý spúšťací skript
