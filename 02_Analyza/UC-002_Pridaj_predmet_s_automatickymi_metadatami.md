# Prípad použitia: UC-002 – Pridaj predmet s automatickými metadátami

## Identifikátor:
`UC-002`

------------------------------------------------------------
## Názov:
**Pridaj predmet s automatickými metadátami**

------------------------------------------------------------
## Popis:
Zberateľ zaeviduje nový predmet do svojho portfólia vyhľadaním cez názov alebo kód, pričom systém automaticky stiahne oficiálne fotografie a parametre z verejného API.

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Zberateľ
- **Sekundárny aktér:** Verejné katalógové API (napr. PokéAPI, Discogs API, BGG API)

------------------------------------------------------------
## Vstupné podmienky:
- Zberateľ je prihlásený v systéme s aktívnym používateľským kontom.
- Externé katalógové API je dostupné.

------------------------------------------------------------
## Výstupné podmienky:
- Predmet je uložený v zberateľovom portfóliu so všetkými stiahnutými metadátami, fotografiou, kúpnou cenou a stavom.
- Celková hodnota portfólia zberateľa je okamžite prepočítaná.

------------------------------------------------------------
## Spúšťač (Trigger):
Zberateľ klikne na tlačidlo „Pridať nový predmet do zbierky“ v používateľskom rozhraní.

------------------------------------------------------------
## Hlavný scenár:
1. Zberateľ otvorí formulár pridania a do vyhľadávacieho poľa zadá kľúčové slovo, oficiálny názov alebo naskenuje čiarový kód.
2. Systém odošle dotaz na externé verejné API pre dohľadanie zodpovedajúcich položiek.
3. Systém prijme výsledky a zobrazí používateľovi zoznam nájdených oficiálnych položiek vrátane miniatúr fotografií.
4. Zberateľ označí zodpovedajúci predmet zo zoznamu.
5. Systém automaticky predvyplní formulár metadátami: oficiálny názov, kategória, rok vydania, výrobca/séria a oficiálna fotografia.
6. Zberateľ zadá špecifické údaje svojej fyzickej položky: reálny stav (napr. Mint, Near Mint), skutočnú nákupnú cenu a vlastnú poznámku.
7. Zberateľ potvrdí uloženie formulára kliknutím na „Uložiť do zbierky“.
8. Systém zapíše predmet do databázy a vykoná okamžitý prepočet celkovej hodnoty portfólia.

------------------------------------------------------------
## Alternatívne scenáre:
**2a – Externé verejné API je dočasne nedostupné alebo zlyhalo spojenie**
2a.1 Systém zobrazí informačnú správu: „Externé API nie je momentálne dostupné. Môžete pokračovať manuálnym zadaním údajov.“
2a.2 Systém prepne formulár do plne manuálneho režimu umožňujúceho nahrať vlastnú fotografiu z disku.
2a.3 Use case pokračuje krokom 6 v manuálnom režime.
**3a – Pre zadané kľúčové slovo sa nenašli žiadne položky v API**
3a.1 Systém oznámi zberateľovi: „Pre zadaný výraz nebol nájdený žiadny oficiálny záznam.“
3a.2 Používateľ buď upraví vyhľadávací dotaz (návrat ku kroku 1), alebo zvolí možnosť manuálneho vytvorenia.
