# Testovacie scenáre a výsledky testov (Test Specification & Results)

V súlade s RUP metodikou tento dokument definuje formálne testovacie scenáre pre overenie funkčnej správnosti systému **Zbierka**, ich vstupy, očakávané výstupy, skutočné výsledky a register vyriešených chýb.

---

## 1. Prehľad testovacích scenárov

| Kód testu | Testovaný Use Case / Modul | Účel testu | Typ testu | Výsledok |
| :--- | :--- | :--- | :---: | :---: |
| **TC-001** | UC-001: Registrácia | Overenie vytvorenia nového konta a hesla | Integračný | **ÚSPEŠNÝ (PASS)** |
| **TC-002** | UC-001: Duplicitný e-mail | Overenie odmietnutia existujúceho e-mailu | Hraničný | **ÚSPEŠNÝ (PASS)** |
| **TC-003** | UC-002: API vyhľadávanie | Automatické doplnenie metadát z verejného API | Komponentový | **ÚSPEŠNÝ (PASS)** |
| **TC-004** | UC-002: Neznámy dotaz API | Správne prepnutie na manuálny formulár | Výnimkový | **ÚSPEŠNÝ (PASS)** |
| **TC-005** | UC-004: Bot filtrovanie | Cenový strop a vyradenie vylučovacích slov | Jednotkový | **ÚSPEŠNÝ (PASS)** |
| **TC-006** | UC-005: Interaktívna notifikácia | Vytvorenie notifikácie pri zhode inzerátu | Systémový | **ÚSPEŠNÝ (PASS)** |
| **TC-007** | UC-005: Automatický zápis | Zápis inzerátu do DB a prepočet hodnoty (Quick Add) | Akceptačný | **ÚSPEŠNÝ (PASS)** |

---

## 2. Podrobné testovacie scenáre

### TC-003: Automatické načítanie metadát z verejného API
- **Viazaný Use Case:** UC-002 (Pridaj predmet s automatickými metadátami)
- **Vstupné podmienky:** Služba `PublicCatalogApiService` je inicializovaná.
- **Testovacie vstupy:** Vyhľadávací reťazec `"Charizard base set"`.
- **Očakávaný výstup:**
  - `success == True`
  - Nájdený oficiálny názov obsahuje `"Charizard #4 Base Set"`
  - Foto URL nie je prázdne a obsahuje odkaz na platný obrázok
  - Odhadovaná cena je kladné číslo (1 250,00 €)
- **Skutočný výstup:** Úspešne stiahnuté všetky atribúty, foto URL `"https://images.pokemontcg.io/base1/4_hires.png"`, cena `1250.00 €`.
- **Záver:** **PASS (Úspešný)**

---

### TC-005: Filtrovanie ponúk autonómnym botom
- **Viazaný Use Case:** UC-004 (Nastav autonómneho monitorovacieho bota)
- **Vstupné podmienky:** Filter nastavený na: `keywords="Charizard base set"`, `max_price=150.00 €`, `exclude_words=["reprint", "proxy", "obal"]`.
- **Testovacie vstupy (3 testovacie ponuky):**
  1. *"Charizard base set obal na kartu"* za 10 € (Obsahuje vylučovacie slovo "obal")
  2. *"Charizard base set holo karta 1999 original"* za 85 € (Spĺňa všetky kritériá)
  3. *"Charizard base set psa 10"* za 2 500 € (Prekračuje strop 150 €)
- **Očakávaný výstup:**
  - Inzerát 1 je ignorovaný (vylučovacie slovo).
  - Inzerát 2 je akceptovaný ako relevantný match.
  - Inzerát 3 je ignorovaný (príliš vysoká cena).
  - Počet akceptovaných ponúk je presne 1.
- **Skutočný výstup:** Bot správne zachytil výhradne inzerát č. 2.
- **Záver:** **PASS (Úspešný)**

---

### TC-007: Automatický zápis z notifikácie a okamžitý prepočet hodnoty zbierky
- **Viazaný Use Case:** UC-005 (Pridaj nájdený predmet z interaktívnej notifikácie – Kľúčová vlastnosť)
- **Vstupné podmienky:** Portfólio má 2 položky v celkovej kúpnej cene 820,00 € a trhovej hodnote 1 030,00 €. Notifikácia #1 je v stave `PENDING`.
- **Testovacie vstupy:** Používateľ vyvolá `handle_quick_add_interaction(notification_id=1)`.
- **Očakávaný výstup:**
  - `result["success"] == True`
  - Počet položiek v databáze narastie na 3.
  - Nová kúpna cena narastie presne o cenu inzerátu (+85,00 € -> 905,00 €).
  - Nová trhová hodnota sa okamžite prepočíta (1 030,00 € + 123,25 € = 1 153,25 €).
  - Stav notifikácie sa zmení na `ACCEPTED`.
- **Skutočný výstup:** Predmet zapísaný do databázy, hodnota okamžite prepočítaná na 1 153,25 €, notifikácia označená ako `ACCEPTED`.
- **Záver:** **PASS (Úspešný)**

---

## 3. Register nájdených a vyriešených chýb (Defect Log)

| ID chyby | Závažnosť | Popis chyby | Spôsob opravy | Stav |
| :--- | :---: | :--- | :--- | :---: |
| **BUG-01** | Stredná | Delenie nulou pri výpočte ROI % ak je nákupná cena zbierky 0 € (nové prázdne konto). | Doplnená podmienka overenia `total_purchase > 0` s návratom `0.0 %`. | **VYRIEŠENÉ** |
| **BUG-02** | Nízka | Vylučovacie slová bota rozlišovali veľké a malé písmená (Case Sensitivity). | Všetky porovnávané reťazce upravené na `.lower()` normalizáciu. | **VYRIEŠENÉ** |
| **BUG-03** | Vysoká | Možnosť opakovaného kliknutia na tlačidlo notifikácie a duplicitného zápisu tej istej položky. | Doplnená kontrola stavu `notif.status == 'PENDING'`, pri druhom kliknutí vráti `success: False`. | **VYRIEŠENÉ** |
