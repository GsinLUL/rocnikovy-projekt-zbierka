# Prípad použitia: UC-006 – Spravuj scrapery a monitoruj systém

## Identifikátor:
`UC-006`

------------------------------------------------------------
## Názov:
**Spravuj scrapery a monitoruj systém**

------------------------------------------------------------
## Popis:
Administrátor monitoruje stav bežiacich botov, kontroluje systémovú záťaž, upravuje intervaly dopytovania trhovísk a spravuje API tokeny.

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Administrátor systému
- **Sekundárny aktér:** Scraper worker daemony, API manažér

------------------------------------------------------------
## Vstupné podmienky:
- Používateľ je prihlásený s rolou Administrátor.

------------------------------------------------------------
## Výstupné podmienky:
- Konfiguračné zmeny botov sú uložené a ihneď aplikované bežiacimi procesmi.
- Systémové logy a štatistiky sú aktualizované.

------------------------------------------------------------
## Spúšťač (Trigger):
Administrátor vstúpi do administračného rozhrania systému.

------------------------------------------------------------
## Hlavný scenár:
1. Administrátor otvorí sekciu „Správa botov a systémový monitoring“.
2. Systém zobrazí dashboard so zoznamom bežiacich scraper procesov, počtom vybavených dotazov za minútu, chybovosťou a vyťažením CPU.
3. Administrátor skontroluje čerpanie limitov (quota) verejných API.
4. Administrátor upraví globálny interval dopytovania pre modul Vinted (napr. predĺženie intervalu z 20s na 45s pre ochranu IP adresy).
5. Administrátor uloží novú konfiguráciu.
6. Systém prepošle signál bežiacim workerom a zaznamená zmenu do audítorského logu.
7. Systém zobrazí potvrdenie o úspešnej rekonfigurácii workerov bez výpadku služby.

------------------------------------------------------------
## Alternatívne scenáre:
**2a – Jeden z bežiacich scraper botov havaroval alebo zamrzol**
2a.1 Systém zobrazí stav workera v červenej farbe s chybovým popisom (Crash / Timeout).
2a.2 Administrátor klikne na akciu „Reštartovať worker“.
2a.3 Systém inicializuje novú inštanciu procesu a obnoví monitorovanie.
