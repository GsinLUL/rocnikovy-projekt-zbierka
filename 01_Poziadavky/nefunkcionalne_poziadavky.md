# Nefunkcionálne požiadavky (Non-Functional Requirements)

Nefunkcionálne požiadavky definujú požadované kvalitatívne atribúty, prevádzkové vlastnosti a obmedzenia systému.  
Kategorizácia a formulácie striktne reflektujú prednášku **Analýza - Zber požiadaviek**:
- **Výkonnosť (Performance):** NFR-P-xx
- **Dostupnosť (Availability):** NFR-A-xx
- **Bezpečnosť (Security):** NFR-S-xx
- **Použiteľnosť (Usability):** NFR-U-xx
- **Škálovateľnosť (Scalability):** NFR-SC-xx
- **Udržiavateľnosť (Maintainability):** NFR-B-xx

Tieto požiadavky sú identicky zaznamenané aj v tabuľke `poziadavky-SABLONA.xlsx` na liste *Nefunkcionálne požiadavky*.

---

### 1. Výkonnosť (Performance)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-P-01** | Systém musí načítať a zobraziť portfólio používateľa so zoznamom predmetov do 2 sekúnd od odoslania požiadavky pri bežnom zaťažení. | **M** |
| **NFR-P-02** | Systém by mal vygenerovať a doručiť interaktívnu notifikáciu používateľovi do 30 sekúnd od momentu zverejnenia inzerátu na monitorovanom trhovisku. | **S** |
| **NFR-P-03** | Systém by mohol vrátiť doplnené metadáta a fotografie z externého API do 1 sekundy vďaka lokálnemu medzipamäťovému cachovaniu často dopytovaných položiek. | **C** |
| **NFR-P-04** | Systém nebude garantovať odozvu pod 100 milisekúnd pri komplexných analytických prepočtoch histórie trhových cien obsahujúcich viac než 50 000 záznamov. | **W** |

---

### 2. Dostupnosť (Availability)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-A-01** | Systém musí zabezpečiť dostupnosť webového a mobilného rozhrania minimálne 99,0 % času ročne (mimo vopred oznámených plánovaných servisných odstávok). | **M** |
| **NFR-A-02** | Systém by mal zabezpečiť nepretržitý beh autonómneho monitorovacieho skriptu (bota) s dostupnosťou minimálne 99,5 % času a automatickým reštartom workeru pri neočakávanom páde. | **S** |
| **NFR-A-03** | Systém by mohol dosahovať dostupnosť 99,9 % nasadením v multi-zónovej cloudovej infraštruktúre s automatickým prepínaním záťaže (failover). | **C** |
| **NFR-A-04** | Systém nebude garantovať nepretržitú dostupnosť bez akýchkoľvek plánovaných odstávok (nebude vyžadovaný režim 100% zero-downtime údržby). | **W** |

---

### 3. Bezpečnosť (Security)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-S-01** | Systém musí šifrovať všetku sieťovú komunikáciu pomocou protokolu TLS 1.3 (HTTPS, WSS) a ukladať používateľské heslá vo forme kryptografického hashu so soľou (napr. Argon2 alebo bcrypt). | **M** |
| **NFR-S-02** | Systém by mal bezpečne spravovať prístupové tokeny k externým API a scraping session cookies v zašifrovanom centrálnom trezore tajomstiev (Secrets Vault / Environment variables). | **S** |
| **NFR-S-03** | Systém by mohol automaticky detegovať podozrivé pokusy o prihlásenie z nových zariadení alebo geolokácií a vyžadovať dodatočné potvrdenie cez e-mail. | **C** |
| **NFR-S-04** | Systém nebude uchovávať žiadne platobné údaje používateľov (čísla kreditných kariet, CVV kódy), nakoľko nerealizuje finančné transakcie. | **W** |

---

### 4. Použiteľnosť (Usability)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-U-01** | Systém musí poskytovať responzívne a intuitívne používateľské rozhranie umožňujúce pridanie nájdeného predmetu do zbierky maximálne na 1 interakciu (kliknutie na tlačidlo v notifikácii). | **M** |
| **NFR-U-02** | Systém by mal spĺňať štandardy prístupnosti webového obsahu podľa metodiky WCAG 2.1 na úrovni AA vrátane čitateľného kontrastu a klávesovej navigácie. | **S** |
| **NFR-U-03** | Systém by mohol ponúkať interaktívnu nápovedu (onboarding sprievodcu) pre nového používateľa s vysvetlením konfigurácie monitorovacieho bota. | **C** |
| **NFR-U-04** | Systém nebude poskytovať hlasové ovládanie používateľského rozhrania ani špecializované textové terminálové rozhranie (CLI) pre koncových zberateľov. | **W** |

---

### 5. Škálovateľnosť (Scalability)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-SC-01** | Systém musí zvládnuť súčasnú obsluhu minimálne 1 000 aktívnych používateľov a evidenciu 100 000 položiek v databáze bez degradácie rýchlosti odozvy. | **M** |
| **NFR-SC-02** | Systém by mal umožniť horizontálne škálovanie monitorovacích botov pomocou kontajnerizácie (Docker workerov) pri zvýšení počtu sledovaných trhovísk. | **S** |
| **NFR-SC-03** | Systém by mohol automaticky škálovať výpočtové prostriedky databázového servera na základe aktuálnej záťaže dopytov (cloud auto-scaling). | **C** |
| **NFR-SC-04** | Systém nebude v prvej verzii dimenzovaný na masívnu prevádzku presahujúcu 1 000 000 súčasne pripojených používateľov (enterprise Big Data škála). | **W** |

---

### 6. Udržiavateľnosť (Maintainability)
| ID | Požiadavka | MoSCoW |
| :--- | :--- | :---: |
| **NFR-B-01** | Systém musí mať modularizovaný a zdokumentovaný zdrojový kód s jasným oddelením frontendovej aplikácie, backendového API a autonómneho bota. | **M** |
| **NFR-B-02** | Systém by mal dosahovať minimálne 70 % pokrytie kľúčovej biznis logiky (výpočet hodnoty, obsluha notifikácií, scraping parsery) automatizovanými unit testami. | **S** |
| **NFR-B-03** | Systém by mohol využívať plne automatizovanú CI/CD pipeline pre priebežnú integráciu, statickú analýzu kódu a nasadzovanie do testovacieho prostredia. | **C** |
| **NFR-B-04** | Systém nebude vyžadovať manuálnu úpravu zdrojového kódu ani reštart celého servera pri zmene vyhľadávacích kritérií pre bežných používateľov. | **W** |
