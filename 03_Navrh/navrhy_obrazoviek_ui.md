# Návrhy obrazoviek a používateľského rozhrania (UI Wireframes)

V súlade s RUP metodikou tento dokument predstavuje konceptuálne náčrty (wireframes) kľúčových obrazoviek systému **Zbierka** pre webové aj mobilné rozhranie.

---

## 1. Obrazovka 1: Prehľad portfólia (Dashboard & Portfolio View)
Hlavná obrazovka zberateľa po prihlásení. Zobrazuje celkovú hodnotu zbierky, zisk/stratu, graf vývoja a zoznam predmetov.

```
+---------------------------------------------------------------------------------------+
|  [LOGO] ZBIERKA        Portfólio    Cenové trendy    Monitor bot (3)      [Zberateľ v] |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +--------------------------+  +--------------------------+  +-------------------+   |
|   | CELKOVÁ HODNOTA ZBIERKY  |  | CELKOVÝ ZISK (ROI)       |  | POČET POLOŽIEK    |   |
|   | 4 850,00 €               |  | + 1 240,00 € (+34.3 %)   |  | 142 ks            |   |
|   +--------------------------+  +--------------------------+  +-------------------+   |
|                                                                                       |
|   VÝVOJ TRHOVEJ HODNOTY V ČASE                 [ 1M | 3M | 6M | 1R | VŠETKO ]         |
|   +-------------------------------------------------------------------------------+   |
|   |   5000 € |                                                      .---* (4 850 €)|   |
|   |   4000 € |                                            .--------'              |   |
|   |   3000 € |                       .-------------------'                        |   |
|   |   2000 € |        .-------------'                                             |   |
|   |   1000 € |_______'                                                            |   |
|   |          Jan 2026      Apr 2026       Jul 2026       Okt 2026                 |   |
|   +-------------------------------------------------------------------------------+   |
|                                                                                       |
|   MOJE PREDMETY                                     [ + Pridať predmet s API ]        |
|   Hľadať: [_______________]  Kategória: [Všetky v]   Zoradiť: [Najvyššia hodnota v]   |
|   +-------------------------------------------------------------------------------+   |
|   | [FOTO] | Charizard 1st Edition Base Set       | Kúpené:  450 € | Trh: 1 200 € | v |
|   | [FOTO] | Black Lotus (Unlimited)              | Kúpené: 1800 € | Trh: 2 400 € | v |
|   | [FOTO] | Lego Star Wars UCS Millennium Falcon | Kúpené:  700 € | Trh:   850 € | v |
|   | [FOTO] | Pikachu Illustrator Promo (Reprint)  | Kúpené:  120 € | Trh:   180 € | v |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
```

---

## 2. Obrazovka 2: Pridanie predmetu s automatickým API obohatením
Používateľ zadá kľúčové slovo alebo kód, API stiahne dáta a predvyplní formulár. Zberateľ doplní len stav a kúpnu cenu.

```
+---------------------------------------------------------------------------------------+
|  PRIDAŤ NOVÝ PREDMET DO ZBIERKY                                                       |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   1. Automatické vyhľadanie cez Verejné API:                                          |
|   Hľadaný výraz / Kód: [ Charizard Base Set               ]  [ Hľadať cez API ]       |
|                                                                                       |
|   Nájdené oficiálne záznamy z API:                                                    |
|   +-------------------------------------------------------------------------------+   |
|   | (*) [FOTO] Charizard #4 - Base Set (1999) - Wizards of the Coast  [Vybrať toto] |   |
|   | ( ) [FOTO] Dark Charizard #4 - Team Rocket (2000)                                 |   |
|   +-------------------------------------------------------------------------------+   |
|                                                                                       |
|   2. Automaticky doplnené metadáta (z API):                                           |
|   Názov položky:    [ Charizard #4 Base Set                     ]                     |
|   Kategória:        [ Pokémon TCG > Wizards of the Coast        ]                     |
|   Rok vydania:      [ 1999                ] Rarita: [ Holo Rare ]                     |
|   Oficiálne foto:   [ https://api.cards.io/images/base4.png     ] [ Náhľad stiahnutý ]|
|                                                                                       |
|   3. Špecifické údaje vašej položky:                                                  |
|   Fyzický stav:     [ Near Mint (NM)                 v ]                              |
|   Vaša kúpna cena:  [ 350.00 ] EUR                                                    |
|   Odhad trhu:       [ 1 100.00 ] EUR (automaticky doporučené z trhu)                  |
|   Poznámka:         [ Kúpené na burze v Bratislave, vložené v magnetickom obale ]     |
|                                                                                       |
|   [ Zrušiť ]                                           [ ULOŽIŤ PREDMET DO ZBIERKY ]  |
+---------------------------------------------------------------------------------------+
```

---

## 3. Obrazovka 3: Konfigurácia monitorovacieho bota (Vinted Scraper)
Zberateľ si definuje strážne pravidlá pre autonómneho bota.

```
+---------------------------------------------------------------------------------------+
|  SPRÁVA MONITOROVACIEHO BOTA (AUTONÓMNY SCRAPER)                                      |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   NOVÉ PRAVIDLO MONITOROVANIA:                                                        |
|   Kľúčové slová:     [ Charizard Base Set holo                                 ]      |
|   Cieľové trhovisko: [ Vinted                                               v ]      |
|   Maximálna cena:    [ 150.00 ] EUR  (inzeráty nad túto sumu budú ignorované)         |
|   Vylučovacie slová: [ reprint, proxy, poskodena, poskodeny, obal               ]      |
|   Frekvencia kontroly:[ Každých 30 sekúnd                                    v ]      |
|   Notifikácie:       [*] Mobil Push    [*] Web banner    [ ] E-mail                   |
|                                                                                       |
|                                                   [ + AKTIVOVAŤ MONITOROVANIE ]       |
|                                                                                       |
|   AKTÍVNE PRAVIDLÁ SLEDOVANIA (2/10):                                                 |
|   +-------------------------------------------------------------------------------+   |
|   | Kľúčové slová         | Trh    | Max. cena | Nájdených | Stav       | Akcie       |   |
|   |-----------------------|--------|-----------|-----------|------------|-------------|   |
|   | Charizard Base Set    | Vinted |  150.00 € | 4 ponuky  | [BEŽÍ OK]  | [Pauza] [X] |   |
|   | Black Lotus MTG       | Vinted | 1200.00 € | 0 ponúk   | [BEŽÍ OK]  | [Pauza] [X] |   |
|   +-------------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------------+
```

---

## 4. Obrazovka 4: Interaktívna notifikácia a automatické pridanie (Kľúčová vlastnosť)
Pri detekcii nového inzerátu sa zobrazí modálne okno alebo push banner. Jedným kliknutím sa predmet zaeviduje a hodnota prepočíta.

```
+---------------------------------------------------------------------------------------+
|  !!! DETEGOVANÝ VÝHODNÝ INZERÁT NA VINTED !!!                                  [ X ]  |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +--------------+   Názov inzerátu:                                                  |
|   |              |   Pokemon Charizard Base Set Holo card rare orig                   |
|   |    [FOTO     |                                                                    |
|   |   PREDMETU   |   Predajná cena:  85,00 €  (Trhový odhad: 400 €)                   |
|   |   Z VINTED]  |   Predajca:       kolektor99 (Hodnotenie: 5.0 ★★★★★)               |
|   |              |   Lokalita:       Slovensko / Česko                                |
|   +--------------+   Zverejnené:     pred 24 sekundami                                |
|                                                                                       |
|   ---------------------------------------------------------------------------------   |
|   Chcete tento predmet zaevidovať do svojej zbierky?                                  |
|                                                                                       |
|      [ Zobraziť na Vinted ]         [ Ignorovať ]         [ ★ PRIDAŤ DO ZBIERKY ]     |
|                                                                                       |
+---------------------------------------------------------------------------------------+
                                           │
                        (Po kliknutí na "PRIDAŤ DO ZBIERKY")
                                           ▼
+---------------------------------------------------------------------------------------+
|  [✓] PREDMET ÚSPEŠNE ZAPÍSANÝ DO ZBIERKY!                                             |
|  Nová celková hodnota vašej zbierky bola prepočítaná na: 4 935,00 € (+85,00 €)        |
+---------------------------------------------------------------------------------------+
```
