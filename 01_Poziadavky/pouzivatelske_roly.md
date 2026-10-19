# Používateľské roly (Actors / User Roles)

V súlade s teóriou zberu požiadaviek reprezentuje každá rola zoskupenie používateľov s rovnakými úlohami, zodpovednosťami a právami vo vzťahu k systému.

---

## 1. Zberateľ (Collector / Registrovaný používateľ)
- **Charakteristika:** Primárny koncový používateľ systému. Vlastní fyzickú alebo digitálnu zbierku predmetov a aktívne vyhľadáva nové prírastky na sekundárnych trhoch.
- **Hlavné činnosti a práva:**
  - Registrácia, prihlásenie a správa svojho profilu (voľba meny, notifikačných kanálov).
  - Pridávanie, editácia a mazanie predmetov vo svojom portfóliu.
  - Vyhľadávanie predmetov v katalógu a automatické sťahovanie metadát z verejných API.
  - Zobrazovanie cenových grafov, histórie a celkového zhodnotenia svojho portfólia.
  - Nastavovanie a správa vlastných pravidiel monitorovania pre autonómneho bota (kľúčové slová, cenové stropy).
  - Prijímanie interaktívnych notifikácií a potvrdenie automatického pridania nájdeného predmetu do zbierky jedným kliknutím.

---

## 2. Neregistrovaný návštevník (Guest / Visitor)
- **Charakteristika:** Používateľ, ktorý zatiaľ nemá vytvorené konto a navštívil webovú alebo mobilnú aplikáciu.
- **Hlavné činnosti a práva:**
  - Prezeranie úvodnej stránky s popisom funkcií aplikácie.
  - Vytvorenie nového používateľského konta (registrácia).
  - Prihlásenie do existujúceho konta alebo vyžiadanie odkazu na obnovu zabudnutého hesla.

---

## 3. Administrátor systému (System Administrator)
- **Charakteristika:** Používateľ zodpovedný za technický dohľad, infraštruktúru a prevádzkovú stabilitu systému.
- **Hlavné činnosti a práva:**
  - Monitorovanie stavu bežiacich monitorovacích botov (workerov) a prideľovanie systémových zdrojov.
  - Konfigurácia prístupových kľúčov k externým API a monitorovanie ich spotreby (quota / rate limiting).
  - Nastavovanie globálnych limitov dopytovania pre scraping skripty, aby nedochádzalo k blokovaniu IP adries.
  - Prezeranie chybových logov, audítorských záznamov a bezpečnostných incidentov.

---

## 4. Sekundárne externé roly (Systémoví aktéri)
- **Autonómny monitorovací bot (Worker Daemon):**  
  Periodický proces bežiaci na pozadí, ktorý podľa zadaných používateľských filtrov skenuje trhoviská (Vinted), vyhodnocuje zhodu a generuje notifikačné udalosti.
- **Verejné API (Katalógové služby tretích strán):**  
  Externé webové služby (napr. PokéAPI, Discogs API, BGG API), ktoré na požiadanie poskytujú štandardizované metadáta, parametre a referenčné fotografie.
- **Online trhoviská (napr. Vinted):**  
  Cieľové externé platformy, na ktorých používatelia zverejňujú inzeráty a ktoré autonómny bot skenuje.
