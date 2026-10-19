# Prípad použitia: UC-003 – Zobraz vývoj trhových cien zbierky

## Identifikátor:
`UC-003`

------------------------------------------------------------
## Názov:
**Zobraz vývoj trhových cien zbierky**

------------------------------------------------------------
## Popis:
Zberateľ si v aplikácii zobrazí grafický vývoj trhovej hodnoty jednotlivých predmetov a celkového portfólia v čase vrátane výpočtu zhodnotenia (ROI).

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Zberateľ
- **Sekundárny aktér:** Cenový analytický modul

------------------------------------------------------------
## Vstupné podmienky:
- Zberateľ je prihlásený v systéme.
- V portfóliu zberateľa je zaevidovaný aspoň jeden predmet s priradenými cenovými záznamami.

------------------------------------------------------------
## Výstupné podmienky:
- Používateľovi sú zobrazené interaktívne grafy a sumárne štatistiky vývoja cien portfólia.

------------------------------------------------------------
## Spúšťač (Trigger):
Zberateľ klikne v hlavnej navigácii na položku „Vývoj cien a trhová analytika“.

------------------------------------------------------------
## Hlavný scenár:
1. Zberateľ zvolí požadované časové obdobie sledovania (napr. 1 mesiac, 3 mesiace, 1 rok, celá história).
2. Systém z databázy agreguje historické trhové ceny položiek a porovná ich s pôvodnými nákupnými cenami.
3. Systém vypočíta celkovú hodnotu zbierky, čistý zisk/stratu a percentuálne zhodnotenie (ROI).
4. Systém vygeneruje a vykreslí interaktívny časový graf vývoja cien a zoznam najviac rastúcich predmetov.
5. Zberateľ interaguje s grafom pomocou kurzora a prezerá si konkrétne cenové body v jednotlivých dátumoch.

------------------------------------------------------------
## Alternatívne scenáre:
**2a – Pre vybraný predmet zatiaľ neexistuje dostatok historických dát o trhových cenách**
2a.1 Systém zobrazí informatívny štítok: „Nedostatok historických trhových údajov.“
2a.2 Systém namiesto odhadu trhovej ceny zobrazí nákupnú cenu zberateľa ako východiskovú hodnotu.
2a.3 Systém zaradí položku do prioritného frontu monitorovacieho bota na dohľadanie trhových ponúk.
