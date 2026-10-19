# Opis problému a procesov (Domain Analysis & Business Processes)

Tento dokument v súlade s RUP metodikou analyzuje **problémovú oblasť zberateľstva** a podrobne modeluje biznis procesy systému **Zbierka** ešte pred voľbou konkrétnych technológií.

---

## 1. Analýza problémovej domény

### 1.1 Súčasný stav a problémy zberateľov (As-Is stav)
- **Fragmentácia a manuálna réžia:** Zberatelia si evidujú svoje portfólio v Exceli, tabuľkách Google Sheets alebo v papierových zápisníkoch. Pre každý predmet musia manuálne dohľadávať názov, rok vydania, číslo karty/položky, výrobcu a manuálne ukladať fotografie. Pri stovkách položiek to vedie k vysokej chybovosti a odrádza zberateľov od udržiavania aktuálnej evidencie.
- **Vysoká volatilita trhových cien:** Ceny zberateľských predmetov na sekundárnych trhoch kolíšu v závislosti od dopytu, trendov a stavu ponuky. Zberateľ bez automatizovaných nástrojov nemá prehľad o reálnej celkovej hodnote svojej zbierky ani o tom, ktoré kusy získavajú na hodnote (ROI).
- **Problém sekundárnych trhovísk (Trhová asymetria):** Na online trhoviskách ako Vinted, Bazoš alebo eBay sa výhodné ponuky od predajcov (ktorí nepoznajú presnú trhovú hodnotu) objavujú náhodne v priebehu dňa. Tieto inzeráty bývajú kúpené v priebehu sekúnd až minút. Bežný používateľ nemá čas neustále manuálne obnovovať vyhľadávanie.
- **Oddelenosť nákupného a evidenčného procesu:** Aj keď zberateľ úspešne nájde a kúpi predmet cez inzerát, musí následne otvoriť svoju evidenciu, znova celý predmet vypísať, dohľadať obrázky a manuálne prepočítať novú hodnotu portfólia.

---

## 2. Navrhované riešenie (To-Be procesy)

Systém **Zbierka** prepája dve zložky do jedného uceleného ekosystému:
1. **Databázové portfólio s napojením na verejné API:** Automatizuje obohacovanie dát a odstraňuje manuálne vypisovanie.
2. **Autonómny monitorovací bot s okamžitou notifikáciou a prepojením:** Nepretržite sleduje trh a umožňuje zápis do zbierky na jedno kliknutie.

```
       [ Zberateľ ]
            │
            ├─► 1. Nastaví kľúčové slová a max. cenu ────────┐
            │                                                │
            │                                                ▼
            │                                     ┌───────────────────────┐
            │                                     │ Autonómny monitor bot │
            │                                     └──────────┬────────────┘
            │                                                │ 2. Nepretržite skenuje
            │                                                ▼
            │                                     ┌───────────────────────┐
            │                                     │ Trhovisko (napr.      │
            │                                     │ Vinted)               │
            │                                     └──────────┬────────────┘
            │                                                │ 3. Detegovaný inzerát
            │                                                ▼
            │◄─ 4. Doručená interaktívna notifikácia ────────┤
            │      (foto, cena, tlačidlo "Pridať")           │
            │                                                │
            ├─► 5. Kliknutie: "Pridať do zbierky" ───────────┤
            │                                                │
            │                                                ▼
            │                                     ┌───────────────────────┐
            │                                     │ Databáza portfólia    │
            │                                     │ + Prepočet hodnoty    │
            │                                     └───────────────────────┘
```

---

## 3. Detailný proces automatického obohatenia dát z verejného API
1. Zberateľ zadá identifikačný kľúč (názov, EAN kód, číslo setu).
2. Systém vyvolá verejné API (napr. PokéAPI, Discogs API, BoardGameGeek API).
3. API vráti štruktúrovaný JSON payload:
   - Oficiálny plný názov položky,
   - Dátum / rok vydania a edíciu,
   - URL oficiálnej fotografie vo vysokom rozlíšení,
   - Atribúty (výrobca, rarita, číslo položky v sérii).
4. Systém predvyplní polia formulára a stiahne referenčnú fotografiu.
5. Zberateľ doplní len vlastné špecifické dáta (reálny stav: nový/používaný, kúpnu cenu).
6. Predmet je uložený bez akejkoľvek zdĺhavej manuálnej práce.

---

## 4. Proces monitorovania trhu a okamžitého prepočtu (Kľúčová vlastnosť)
1. **Skenovacia slučka:** Autonómny bot periodicky dopytuje verejné endpoints / RSS / zoznam ponúk na Vinted v náhodných intervaloch chrániacich pred blokovaním IP.
2. **Filtračný filter:** Prijaté inzeráty sa filtrujú cez zberateľom zadané kľúčové slová, cenový strop a negatívne vylučovacie slová.
3. **Udalosť zhody (Match Event):** Ak inzerát spĺňa všetky podmienky, vytvorí sa záznam udalosti a odošle sa interaktívna notifikácia (Push/Web/Email).
4. **Interaktívna akcia používateľa:** Notifikácia obsahuje priame akčné tlačidlo: *„Pridať do zbierky za X €“*.
5. **Transakčný zápis a prepočet:**
   - Po kliknutí sa inzerát ihneď zapíše do tabuľky používateľských predmetov.
   - Databázový trigger / servisná metóda okamžite agreguje hodnoty všetkých položiek používateľa:
     $$\text{Celková hodnota} = \sum_{i=1}^{n} \text{Aktuálna hodnota}_i$$
   - Používateľ vidí okamžitú aktualizáciu stavu svojho celkového majetku v zbierke.
