# Architektúra a rozdelenie aplikácie (System Architecture)

V súlade s RUP metodikou tento dokument definuje technickú architektúru, komponentové členenie a dátové toky systému **Zbierka**.

---

## 1. Celkový architektonický štýl
Systém je navrhnutý ako **modulárna vrstvená architektúra** s prvkami **udalosťami riadenej architektúry (Event-Driven Architecture)** pre asynchrónne spracovanie notifikácií a scrapingových úloh.

Systém striktne oddeľuje dva hlavné autonómne subsystémy:
1. **Modul A: Aplikačný server a databázové portfólio (Web / Mobil / API Backend)**
2. **Modul B: Autonómny monitorovací a scraping subsystém (Worker Bots)**

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Klientska vrstva (Frontend)                     │
│   ┌───────────────────────────────┐  ┌──────────────────────────────┐  │
│   │    Responzívna Web Aplikácia  │  │   Mobilné Rozhranie (PWA)    │  │
│   └───────────────┬───────────────┘  └──────────────┬───────────────┘  │
└───────────────────┼─────────────────────────────────┼──────────────────┘
                    │ HTTPS (REST API / WebSocket)     │
┌───────────────────▼─────────────────────────────────▼──────────────────┐
│                   Backend & Aplikačná logika (Modul A)                 │
│   ┌─────────────────┐ ┌──────────────────┐ ┌────────────────────────┐  │
│   │  Auth & Users   │ │ Portfolio Engine │ │ Price & Analytics Serv │  │
│   └────────┬────────┘ └────────┬─────────┘ └───────────┬────────────┘  │
│            │                   │                       │               │
│            ▼                   ▼                       ▼               │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │             Centrálna Relačná Databáza (PostgreSQL)             │  │
│   └────────────────────────────▲────────────────────────────────────┘  │
│                                │                                       │
│   ┌────────────────────────────┴────────────────────────────────────┐  │
│   │     Event & Notifikačný Engine (WebSockets / Push / Email)      │  │
│   └────────────────────────────▲────────────────────────────────────┘  │
└────────────────────────────────┼───────────────────────────────────────┘
                                 │ Interné Eventy / IPC
┌────────────────────────────────┴───────────────────────────────────────┐
│              Autonómny Monitorovací Subsystém (Modul B)                 │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │ Plánovač úloh & Manažér workerov (Scheduler & Bot Manager)      │  │
│   └────────────────────────────┬────────────────────────────────────┘  │
│                                │ Spúšťa workerov                       │
│              ┌─────────────────┴─────────────────┐                     │
│              ▼                                   ▼                     │
│   ┌─────────────────────────┐         ┌─────────────────────────┐      │
│   │  Vinted Scraper Worker  │         │ Verejné API Katalóg     │      │
│   │  (Parser, Rate limiter) │         │ (Metadata / Photo Enr.) │      │
│   └──────────┬──────────────┘         └───────────┬─────────────┘      │
└──────────────┼────────────────────────────────────┼────────────────────┘
               │ HTTP / JSON                        │ HTTPS REST
               ▼                                    ▼
    ┌─────────────────────┐              ┌─────────────────────┐
    │  Trhovisko Vinted   │              │  Verejné API Tretích│
    │  (Online inzeráty)  │              │  Strán (PokéAPI...) │
    └─────────────────────┘              └─────────────────────┘
```

---

## 2. Popis komponentov a vrstiev

### 2.1 Klientska vrstva (Frontend)
- **Webové a mobilné rozhranie:** Zamerané na intuitívnu správu portfólia, responzívnosť na všetkých obrazovkách (mobil, tablet, desktop) a podporu offline cachovania kľúčových dát.
- **WebSocket / Push klient:** Udržiava perzistentné spojenie so serverom pre okamžité zobrazenie interaktívnej notifikácie bez nutnosti manuálneho obnovovania stránky.

### 2.2 Aplikačný server a API vrstva (Modul A)
- **Portfolio Engine:** Zabezpečuje CRUD operácie nad zberateľskými predmetmi, správu kategórií, štítkov a okamžitý prepočet celkovej hodnoty zbierky pri akejkoľvek zmene.
- **Price Analytics Service:** Pravidelne prepočítava štatistiky vývoja cien, percentuálny ROI, trendy a generuje dáta pre interaktívne grafy.
- **Enrichment Service:** Komunikuje s verejnými API, sťahuje referenčné fotografie a vypĺňa metadáta bez manuálneho zásahu používateľa.

### 2.3 Autonómny monitorovací subsystém (Modul B)
- **Scheduler & Bot Manager:** Spravuje fond workerov, prideľuje im monitorovacie pravidlá od zberateľov a dynamicky riadi intervaly dopytovania (anti-rate-limiting algoritmus).
- **Vinted Scraper Worker:** Realizuje HTTP dotazy, extrahuje nové ponuky, filtruje ich podľa zadaných kľúčových slov, ceny a vylučovacích výrazov.
- **Event Dispatcher:** Pri zhode vygeneruje udalosť `NEW_LISTING_MATCH` a odošle ju do notifikačného engine.

---

## 3. Kľúčový mechanizmus: Rýchle pridanie (Quick Add Flow)
1. Worker vygeneruje udalosť `NEW_LISTING_MATCH`.
2. Notifikačný engine odošle interaktívny payload do klientskej aplikácie.
3. Používateľ klikne na **„Pridať do zbierky“**.
4. Požiadavka je doručená na endpoint `/api/portfolio/quick-add`:
   - Vytvorí sa nová položka v tabuľke `items`.
   - Vytvorí sa záznam o nákupe v `transactions`.
   - Databázový trigger alebo servisná vrstva okamžite vykoná atomický prepočet sumy portfólia:
     $$\text{TotalValue}_{\text{new}} = \text{TotalValue}_{\text{old}} + \text{ItemPrice}$$
   - WebSocketom sa odošle spätná väzba do používateľského rozhrania, ktoré v reálnom čase zaktualizuje stav peňaženky/portfólia.
