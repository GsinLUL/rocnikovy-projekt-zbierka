# Zbierka – Ročníkový projekt

> **Jednotný nástroj pre zberateľov spájajúci databázové portfólio s autonómnym monitorovacím botom a funkciou automatického pridávania.**

---

## Základné informácie
- **Názov projektu:** Zbierka (Collector App & Bot)
- **Autor:** Maxim
- **Trieda:** 3. ročník
- **Cieľ projektu:** Vytvoriť ucelený softvérový systém pre zberateľov pozostávajúci z dvoch úzko prepojených modulov:
  1. **Databázová aplikácia** (web & mobil) pre správu portfólia s automatickým dopĺňaním metadát a fotografií cez verejné API a sledovaním vývoja trhových cien.
  2. **Autonómny monitorovací skript (bot)**, ktorý nepretržite skenuje online trhoviská (Vinted) a generuje interaktívne notifikácie.
  3. **Kľúčové prepojenie:** Po kliknutí na notifikáciu sa predmet automaticky zapíše do databázy používateľa a okamžite v reálnom čase prepočíta celková hodnota jeho zbierky.

---

## Postup spustenia aplikácie

### 1. Spustenie demonštračného prototypu
Aplikácia nevyžaduje žiadne externé knižnice a je ihneď spustiteľná cez Python 3:

```bash
# Na macOS / Linux:
python3 04_Implementacia/src/main.py

# Na Windows:
python 04_Implementacia\src\main.py
```

### 2. Spustenie automatizovaných testov
```bash
# Na macOS / Linux:
python3 05_Testovanie/test_portfolio.py

# Na Windows:
python 05_Testovanie\test_portfolio.py
```

---

## Adresárová štruktúra ročníkového projektu (Metodika inšpirovaná RUP)

```
zbierka/
├── 01_Poziadavky/                                  # ČO MÁ SYSTÉM ROBIŤ
│   ├── poziadavky-SABLONA.xlsx                    # Požiadavky v MS Excel podľa šablóny (Funkcionálne aj Nefunkcionálne)
│   ├── poziadavky.xlsx                            # Kópia požiadaviek pre rýchly prístup
│   ├── zadanie_a_ciel_projektu.md                 # Podrobný kontext a ciele projektu
│   ├── pouzivatelske_roly.md                      # Roly: Zberateľ, Návštevník, Administrátor
│   ├── funkcionalne_poziadavky.md                 # FR-001 až FR-033 rozdelené do 8 blokov (MoSCoW)
│   └── nefunkcionalne_poziadavky.md               # NFR-P, NFR-A, NFR-S, NFR-U, NFR-SC, NFR-B
│
├── 02_Analyza/                                     # AKO FUNGUJE PROBLÉMOVÁ OBLASŤ
│   ├── opis_problemu_a_procesov.md                # As-Is a To-Be analýza, biznis procesy
│   ├── traceability_matrix.md                     # Mapovanie FR požiadaviek na Use Cases
│   ├── use_case_diagram.puml                      # PlantUML diagram prípadov použitia
│   ├── use_case_diagram.svg                       # Vektorový diagram Use Cases (zobraziteľný v prehliadači)
│   ├── UC-00x_SABLONA.docx                        # Prázdna šablóna prípadu použitia
│   ├── UC-001_Registruj_noveho_zberatela.docx     # Vyplnený Word dokument UC-001
│   ├── UC-002_Pridaj_predmet_s_automatickymi_metadatami.docx # Vyplnený Word dokument UC-002
│   ├── UC-003_Zobraz_vyvoj_trhovych_cien_zbierky.docx        # Vyplnený Word dokument UC-003
│   ├── UC-004_Nastav_autonomneho_monitorovacieho_bota.docx   # Vyplnený Word dokument UC-004
│   ├── UC-005_Pridaj_najdeny_predmet_z_interaktivnej_notifikacie.docx # Vyplnený Word dokument UC-005 (Kľúčová vlastnosť)
│   ├── UC-006_Spravuj_scrapery_a_monitoruj_system.docx        # Vyplnený Word dokument UC-006
│   └── UC-*.md                                    # Markdown verzie všetkých Use Cases pre GitHub/GitLab
│
├── 03_Navrh/                                       # AKO SYSTÉM VYTVORÍME
│   ├── architektura_systemu.md                    # 2-modulová vrstvená a udalosťami riadená architektúra
│   ├── erd_navrh_datovych_struktur.md             # Detailná špecifikácia relačného dátového modelu
│   ├── erd_diagram.puml                           # PlantUML ERD model
│   ├── erd_diagram.svg                            # Vektorový diagram ERD
│   └── navrhy_obrazoviek_ui.md                    # Konceptuálne náčrty (wireframes) všetkých obrazoviek
│
├── 04_Implementacia/                               # FUNKČNÝ ZDROJOVÝ KÓD
│   ├── requirements.txt                           # Špecifikácia závislostí
│   └── src/
│       ├── models.py                              # Dátové modely entít (User, Item, BotFilter, Notification)
│       ├── api_service.py                         # Obohacovanie metadát a fotografií cez verejné API
│       ├── scraper_bot.py                         # Autonómny monitorovací skript pre Vinted s filtrami
│       ├── notification_engine.py                 # Interaktívne notifikácie a automatický prepočet hodnoty
│       └── main.py                                # Spustiteľný demonštračný skript
│
├── 05_Testovanie/                                  # OVERENIE SPRÁVNOSTI
│   ├── testovacie_scenare.md                      # Testovacie scenáre (TC-001..TC-007) a Defect Log
│   └── test_portfolio.py                          # Automatizované unit testy (unittest)
│
├── 06_Dokumentacia/                                # NÁVODY A INŠTALÁCIA
│   ├── instalacna_prirucka.md                     # Postup inštalácie a spustenia pre učiteľa
│   └── pouzivatelsky_navod.md                     # Používateľská príručka zberateľa
│
├── vytvor-rocnikovy-projekt.bat                    # Dávkový skript pre generovanie štruktúry na Windows
├── vytvor-rocnikovy-projekt.sh                     # Shell skript pre generovanie štruktúry na macOS/Linux
├── .gitignore                                     # Ignorované dočasné a systémové súbory
└── README.md                                      # Tento úvodný dokument
```

---

## Publikácia na GitHub / GitLab
Projekt je kompletne pripravený pre verzionovanie v Gite.  
Postup publikovania:
```bash
git init
git add .
git commit -m "Inicializacia rocnikoveho projektu Zbierka (Poziadavky, Analyza, Navrh, Implementacia, Testy, Dokumentacia)"
git branch -M main
git remote add origin <URL_VÁŠHO_GIT_REPOZITÁRA>
git push -u origin main
```
