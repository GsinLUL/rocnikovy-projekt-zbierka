# Prípad použitia: UC-004 – Nastav autonómneho monitorovacieho bota

## Identifikátor:
`UC-004`

------------------------------------------------------------
## Názov:
**Nastav autonómneho monitorovacieho bota**

------------------------------------------------------------
## Popis:
Zberateľ vytvorí a nakonfiguruje monitorovacie pravidlo, podľa ktorého autonómny bot nepretržite skenuje sekundárne trhovisko (Vinted) a hľadá nové inzeráty.

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Zberateľ
- **Sekundárny aktér:** Autonómny monitorovací worker (bot)

------------------------------------------------------------
## Vstupné podmienky:
- Zberateľ je prihlásený v systéme.
- Zberateľ neprekročil stanovený limit aktívnych monitorovacích pravidiel (max 10).

------------------------------------------------------------
## Výstupné podmienky:
- Nové pravidlo monitorovania je uložené v databáze a zaradené do aktívneho plánovacieho radu botov.
- Autonómny bot začne periodicky skenovať trhovisko podľa zadaných parametrov.

------------------------------------------------------------
## Spúšťač (Trigger):
Zberateľ klikne na tlačidlo „Nové monitorovanie inzerátov“ v sekcii Sledovanie trhu.

------------------------------------------------------------
## Hlavný scenár:
1. Zberateľ zadá kľúčové slová hľadaného zberateľského predmetu (napr. „Charizard VMAX Shiny“).
2. Zberateľ vyberie cieľové online trhovisko (napr. Vinted).
3. Zberateľ nastaví maximálny cenový limit (strop) a voliteľne minimálny stav položky.
4. Zberateľ vyplní negatívne vylučovacie slová (napr. „reprint, proxy, prázdny obal“).
5. Zberateľ potvrdí konfiguráciu kliknutím na tlačidlo „Aktivovať sledovanie“.
6. Systém overí vstupné parametre a vytvorí nový záznam v tabuľke sledovacích filtrov.
7. Systém inicializuje monitoring v autonómnom worker procese a informuje používateľa o úspešnej aktivácii.

------------------------------------------------------------
## Alternatívne scenáre:
**3a – Zberateľ zadal neplatnú cenovú hodnotu (záporné číslo alebo nula)**
3a.1 Systém zobrazí chybové hlásenie: „Cenový limit musí byť kladné číslo.“
3a.2 Používateľ opraví hodnotu (návrat ku kroku 3).
**6a – Zberateľ dosiahol limit maximálneho počtu súčasne aktívnych pravidiel**
6a.1 Systém zobrazí hlásenie: „Dosiahli ste maximálny limit (10) monitorovacích pravidiel.“
6a.2 Systém ponúkne možnosť deaktivácie niektorého zo starších pravidiel.
