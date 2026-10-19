# Matica sledovateľnosti požiadaviek (Traceability Matrix)

V súlade s metodikou analýzy a prednáškou **Prípady použitia (Use cases)** zabezpečuje Traceability Matrix obojsmernú väzbu medzi definovanými **funkcionálnymi požiadavkami (FR)** a jednotlivými **prípadmi použitia (UC)**.  
Každá funkcionálna požiadavka je pokrytá aspoň jedným use caseom.

---

| ID požiadavky | Názov / Popis požiadavky | Pokrývajúci Use Case | Primárna rola | MoSCoW |
| :--- | :--- | :--- | :--- | :---: |
| **FR-001** | Registrácia, bezpečné prihlásenie a správa profilu používateľa | **UC-001** (Registruj a prihlás zberateľa) | Zberateľ | **M** |
| **FR-002** | Dvojfaktorová autentifikácia (2FA) a obnova hesla | **UC-001** (Registruj a prihlás zberateľa) | Zberateľ | **S** |
| **FR-003** | Prihlásenie cez externých poskytovateľov identity (OAuth 2.0) | **UC-001** (Registruj a prihlás zberateľa) | Zberateľ | **C** |
| **FR-004** | Vylúčenie multi-user zdieľania jedného účtu v v1 | **UC-001** (Registruj a prihlás zberateľa) | Zberateľ | **W** |
| **FR-005** | Evidencia predmetov v zbierke s kompletnými atribútmi | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **M** |
| **FR-006** | Organizácia do podkategórií, sérií a štítkov (tagov) | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **S** |
| **FR-007** | Export celého portfólia do formátov PDF a CSV | **UC-003** (Zobraz vývoj cien zbierky) | Zberateľ | **C** |
| **FR-008** | Vylúčenie priameho nákupu/predaja cez interný e-shop | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **W** |
| **FR-009** | Automatické načítanie metadát a fotografií cez verejné API | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **M** |
| **FR-010** | Manuálna úprava automatických metadát a vlastné foto | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **S** |
| **FR-011** | Rozpoznanie predmetu skenovaním čiarového kódu (EAN/UPC) | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **C** |
| **FR-012** | Vylúčenie generovania syntetických 3D AI vizualizácií | **UC-002** (Pridaj predmet s metadátami) | Zberateľ | **W** |
| **FR-013** | Evidencia a interaktívna vizualizácia trhových cien v čase | **UC-003** (Zobraz vývoj cien zbierky) | Zberateľ | **M** |
| **FR-014** | Prepočet a zobrazenie zisku/straty (ROI) položiek a zbierky | **UC-003** (Zobraz vývoj cien zbierky) | Zberateľ | **S** |
| **FR-015** | Predikcia cenového trendu a nákupné/predajné odporúčania | **UC-003** (Zobraz vývoj cien zbierky) | Zberateľ | **C** |
| **FR-016** | Vylúčenie právne záväzného finančného oceňovania | **UC-003** (Zobraz vývoj cien zbierky) | Zberateľ | **W** |
| **FR-017** | Autonómne nepretržité skenovanie online trhovísk (Vinted) | **UC-004** (Nastav monitorovacieho bota) | Zberateľ | **M** |
| **FR-018** | Pokročilé parametre filtrovania (vylučovacie slová, stav) | **UC-004** (Nastav monitorovacieho bota) | Zberateľ | **S** |
| **FR-019** | Automatická detekcia duplicitných alebo podozrivých inzerátov | **UC-004** (Nastav monitorovacieho bota) | Zberateľ | **C** |
| **FR-020** | Vylúčenie plnoautomatického nákupu tovaru (auto-buy) | **UC-004** (Nastav monitorovacieho bota) | Zberateľ | **W** |
| **FR-021** | Generovanie interaktívnej notifikácie pri detekcii inzerátu | **UC-005** (Pridaj z interaktívnej notifikácie) | Zberateľ | **M** |
| **FR-022** | Automatický zápis predmetu a okamžitý prepočet hodnoty | **UC-005** (Pridaj z interaktívnej notifikácie) | Zberateľ | **M** |
| **FR-023** | Viacero kanálov notifikácií (push, web, e-mail) a frekvencia | **UC-005** (Pridaj z interaktívnej notifikácie) | Zberateľ | **S** |
| **FR-024** | Notifikácie a interakcia cez externých botov (Telegram/Discord) | **UC-005** (Pridaj z interaktívnej notifikácie) | Zberateľ | **C** |
| **FR-025** | Vylúčenie odosielania notifikácií cez platené SMS | **UC-005** (Pridaj z interaktívnej notifikácie) | Zberateľ | **W** |
| **FR-026** | Responzívne webové a mobilné rozhranie so synchronizáciou | **UC-001** až **UC-005** | Zberateľ | **M** |
| **FR-027** | Optimalizácia pre tablety a podpora tmavého režimu (Dark Mode) | **UC-001** až **UC-005** | Zberateľ | **S** |
| **FR-028** | Offline podpora prezerania zbierky v mobilnom rozhraní | **UC-002**, **UC-003** | Zberateľ | **C** |
| **FR-029** | Vylúčenie vývoja natívnej desktopovej aplikácie | **Systém** | Všetci | **W** |
| **FR-030** | Monitoring scraper botov, správa API kľúčov a logov | **UC-006** (Spravuj scrapery a systém) | Administrátor | **M** |
| **FR-031** | Nastavovanie intervalov a limitov dopytovania (rate limits) | **UC-006** (Spravuj scrapery a systém) | Administrátor | **S** |
| **FR-032** | Administrátorský štatistický dashboard vyťaženia systému | **UC-006** (Spravuj scrapery a systém) | Administrátor | **C** |
| **FR-033** | Vylúčenie prístupu administrátora k nehashovaným heslám | **UC-006** (Spravuj scrapery a systém) | Administrátor | **W** |

---

## Prehľad Use Case pokrytia
- **UC-001:** Pokrýva správu účtov, autentifikáciu a bezpečnosť (FR-001, FR-002, FR-003, FR-004, FR-026, FR-027)
- **UC-002:** Pokrýva evidenciu zbierky, štítkovanie a integráciu s verejnými API (FR-005, FR-006, FR-008, FR-009, FR-010, FR-011, FR-012, FR-028)
- **UC-003:** Pokrýva sledovanie trhových cien, grafy a výpočet zhodnotenia (FR-007, FR-013, FR-014, FR-015, FR-016)
- **UC-004:** Pokrýva konfiguráciu pravidiel autonómneho monitorovacieho bota (FR-017, FR-018, FR-019, FR-020)
- **UC-005 (Kľúčová vlastnosť):** Pokrýva detekciu inzerátu, interaktívnu notifikáciu, automatický zápis do databázy a okamžitý prepočet hodnoty zbierky (FR-021, FR-022, FR-023, FR-024, FR-025)
- **UC-006:** Pokrýva administráciu botov, riadenie rate-limitov, API kľúčov a monitorovanie (FR-030, FR-031, FR-032, FR-033)
