# Prípad použitia: UC-005 – Pridaj nájdený predmet z interaktívnej notifikácie

## Identifikátor:
`UC-005`

------------------------------------------------------------
## Názov:
**Pridaj nájdený predmet z interaktívnej notifikácie**

------------------------------------------------------------
## Popis:
Autonómny bot deteguje nový inzerát na trhovisku, doručí zberateľovi interaktívnu notifikáciu a po interakcii (potvrdení) sa predmet automaticky zapíše do databázy a okamžite prepočíta hodnota zbierky.

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Zberateľ
- **Sekundárny aktér:** Autonómny monitorovací bot, Online trhovisko (Vinted), Portfóliový modul

------------------------------------------------------------
## Vstupné podmienky:
- Autonómny bot je spustený a má aktivované pravidlo pre zberateľa.
- Zberateľ má povolené doručovanie notifikácií v aplikácii.
- Na monitorovanom trhovisku bol publikovaný nový inzerát vyhovujúci filtrom.

------------------------------------------------------------
## Výstupné podmienky:
- Predmet z inzerátu je priamo zapísaný do databázového portfólia zberateľa.
- Celková hodnota celej zbierky je okamžite prepočítaná a zobrazená v reálnom čase.
- Notifikácia je označená ako úspešne spracovaná.

------------------------------------------------------------
## Spúšťač (Trigger):
Autonómny bot deteguje nový zverejnený inzerát na trhovisku Vinted spĺňajúci zberateľove kritériá.

------------------------------------------------------------
## Hlavný scenár:
1. Autonómny bot pri periodickom skenovaní identifikuje novú zhodnú ponuku na trhovisku Vinted.
2. Systém zostaví interaktívnu notifikáciu obsahujúcu: názov položky, predajnú cenu, fotografiu, odkaz na inzerát a akčné tlačidlo „Pridať do zbierky“.
3. Systém doručí interaktívnu notifikáciu zberateľovi na jeho mobilné alebo webové zariadenie.
4. Zberateľ klikne na akčné tlačidlo „Pridať do zbierky“ priamo v rozhraní notifikácie.
5. Systém spracuje požiadavku, extrahuje metadáta inzerátu a vytvorí nový záznam predmetu v osobnej databáze zberateľa.
6. Databázový modul okamžite prepočíta novú celkovú hodnotu zberateľovej zbierky (súčet položiek vrátane nového prírastku).
7. Systém používateľovi zobrazí potvrdzujúce hlásenie s aktualizovanou celkovou sumou portfólia a označí notifikáciu ako spracovanú.

------------------------------------------------------------
## Alternatívne scenáre:
**4a – Zberateľ notifikáciu ignoruje alebo odmietne**
4a.1 Zberateľ klikne na možnosť „Ignorovať“ alebo notifikáciu zatvorí.
4a.2 Systém zaznamená odmietnutie ponuky a predmet nezapíše do zbierky.
4a.3 Use case sa ukončí bez zmeny stavu portfólia.
**5a – Pôvodný inzerát bol medzičasom predajcom zmazaný alebo kúpený iným záujemcom**
5a.1 Systém pri kontrole dostupnosti inzerátu zistí, že ponuka už nie je aktívna.
5a.2 Systém informuje zberateľa: „Pôvodný inzerát už nie je aktívny. Želáte si predmet napriek tomu zaevidovať ako vlastný nákup?“
5a.3 V prípade potvrdenia zberateľom sa záznam uloží; v prípade odmietnutia sa akcia zruší.
