# Návrh dátových štruktúr (ERD – Entity Relationship Diagram)

V súlade s RUP metodikou tento dokument definuje relačný dátový model pre systém **Zbierka**, vrátane atribútov, dátových typov, primárnych/cudzích kľúčov a integritných obmedzení.

---

## 1. Prehľad entít
1. **`users` (Používatelia):** Evidencia zberateľov a administrátorov, ich prihlasovacie údaje a preferencie.
2. **`categories` (Kategórie zbierok):** Stromová štruktúra zberateľských kategórií (napr. Kartové hry -> Pokémon -> Base Set).
3. **`items` (Zberateľské predmety):** Jednotlivé evidované predmety v osobnej zbierke s metadátami, stavom a cenami.
4. **`item_images` (Fotografie predmetov):** Oficiálne fotografie stiahnuté z API aj vlastné autentické fotografie používateľa.
5. **`price_history` (História trhových cien):** Časové rady cien zaznamenaných z trhovísk a verejných API pre analytiku a grafy.
6. **`bot_filters` (Pravidlá monitorovacieho bota):** Používateľské filtre pre autonómneho scrapera (kľúčové slová, cenový strop, vylučovacie slová).
7. **`marketplace_listings` (Nájdené inzeráty):** Záznamy o inzerátoch detegovaných botom na trhoviskách (Vinted).
8. **`notifications` (Interaktívne notifikácie):** Notifikačné správy doručené zberateľovi s väzbou na inzerát a akciou rýchleho pridania.

---

## 2. Podrobná špecifikácia tabuliek

### 2.1 Tabuľka: `users`
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `BIGSERIAL` | **PK** | Jednoznačný identifikátor používateľa |
| `username` | `VARCHAR(50)` | **UNIQUE, NOT NULL** | Prihlasovacie používateľské meno |
| `email` | `VARCHAR(255)` | **UNIQUE, NOT NULL** | Kontaktný a prihlasovací e-mail |
| `password_hash`| `VARCHAR(255)` | **NOT NULL** | Bezpečný kryptografický hash (bcrypt/Argon2) |
| `role` | `VARCHAR(20)` | **NOT NULL, DEFAULT 'COLLECTOR'** | Rola (`COLLECTOR`, `ADMIN`) |
| `currency` | `VARCHAR(3)` | **NOT NULL, DEFAULT 'EUR'** | Preferovaná mena (EUR, USD, GBP) |
| `created_at` | `TIMESTAMP` | **NOT NULL, DEFAULT NOW()** | Dátum registrácie konta |

### 2.2 Tabuľka: `categories`
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | **PK** | ID kategórie |
| `name` | `VARCHAR(100)` | **NOT NULL** | Názov kategórie (napr. "Pokémon TCG", "Lego") |
| `parent_id` | `BIGINT` | **FK -> categories(id), NULL** | Rodičovská kategória (pre hierarchie) |
| `api_provider` | `VARCHAR(50)` | **NULL** | Názov príslušného externého API (napr. 'pokeapi') |

### 2.3 Tabuľka: `items` (Jadro portfólia)
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `BIGSERIAL` | **PK** | Jednoznačný identifikátor predmetu |
| `user_id` | `UUID` / `BIGINT` | **FK -> users(id), NOT NULL** | Vlastník položky |
| `category_id` | `BIGINT` | **FK -> categories(id), NOT NULL** | Zaradenie do kategórie |
| `name` | `VARCHAR(255)` | **NOT NULL** | Názov predmetu |
| `condition` | `VARCHAR(50)` | **NOT NULL** | Fyzický stav (napr. 'Mint', 'Near Mint', 'Good') |
| `purchase_price`| `NUMERIC(10,2)`| **NOT NULL** | Kúpna cena zaevidovaná zberateľom |
| `estimated_value`| `NUMERIC(10,2)`| **NOT NULL** | Aktuálna odhadovaná trhová hodnota |
| `acquired_at` | `DATE` | **NOT NULL, DEFAULT CURRENT_DATE** | Dátum nadobudnutia položky |
| `external_api_id`| `VARCHAR(100)`| **NULL** | Identifikátor v katalógovom API |
| `source_listing_id`| `BIGINT` | **FK -> marketplace_listings(id), NULL** | Referencia na inzerát (ak pridané cez bot) |
| `notes` | `TEXT` | **NULL** | Osobné poznámky zberateľa |

### 2.4 Tabuľka: `price_history`
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | **PK** | ID záznamu |
| `item_id` | `BIGINT` | **FK -> items(id), NOT NULL** | Sledovaný predmet |
| `recorded_price`| `NUMERIC(10,2)`| **NOT NULL** | Zaznamenaná trhová cena |
| `source` | `VARCHAR(50)` | **NOT NULL** | Zdroj ceny ('Vinted', 'Marketplace API', 'User') |
| `recorded_at` | `TIMESTAMP` | **NOT NULL, DEFAULT NOW()** | Časová pečiatka záznamu |

### 2.5 Tabuľka: `bot_filters` (Pravidlá autonómneho bota)
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | **PK** | ID pravidla |
| `user_id` | `UUID` / `BIGINT` | **FK -> users(id), NOT NULL** | Zberateľ, ktorému pravidlo patrí |
| `keywords` | `VARCHAR(255)` | **NOT NULL** | Vyhľadávaný reťazec (napr. "Charizard Base") |
| `max_price` | `NUMERIC(10,2)`| **NOT NULL** | Cenový strop pre inzeráty |
| `exclude_words` | `VARCHAR(255)` | **NULL** | Vylučovacie slová (oddelené čiarkou) |
| `target_market`| `VARCHAR(50)` | **NOT NULL, DEFAULT 'VINTED'**| Cieľové trhovisko |
| `is_active` | `BOOLEAN` | **NOT NULL, DEFAULT TRUE** | Príznak aktívneho sledovania |
| `created_at` | `TIMESTAMP` | **NOT NULL, DEFAULT NOW()** | Dátum vytvorenia pravidla |

### 2.6 Tabuľka: `marketplace_listings`
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | **PK** | ID inzerátu v systéme |
| `external_id` | `VARCHAR(100)` | **NOT NULL** | ID inzerátu na trhovisku (Vinted ID) |
| `title` | `VARCHAR(255)` | **NOT NULL** | Zverejnený titulok inzerátu |
| `price` | `NUMERIC(10,2)`| **NOT NULL** | Predajná cena na trhovisku |
| `currency` | `VARCHAR(3)` | **NOT NULL, DEFAULT 'EUR'** | Mena ponuky |
| `listing_url` | `TEXT` | **NOT NULL** | Priamy odkaz na ponuku |
| `photo_url` | `TEXT` | **NULL** | URL fotografie z inzerátu |
| `detected_at` | `TIMESTAMP` | **NOT NULL, DEFAULT NOW()** | Čas detekcie botom |

### 2.7 Tabuľka: `notifications`
| Stĺpec | Dátový typ | Obmedzenie | Popis |
| :--- | :--- | :--- | :--- |
| `id` | `BIGSERIAL` | **PK** | ID notifikácie |
| `user_id` | `UUID` / `BIGINT` | **FK -> users(id), NOT NULL** | Adresát notifikácie |
| `listing_id` | `BIGINT` | **FK -> marketplace_listings(id)** | Nájdený inzerát |
| `status` | `VARCHAR(20)` | **NOT NULL, DEFAULT 'PENDING'**| Stav (`PENDING`, `ACCEPTED`, `DISMISSED`) |
| `sent_at` | `TIMESTAMP` | **NOT NULL, DEFAULT NOW()** | Čas doručenia |
| `action_taken_at`| `TIMESTAMP`| **NULL** | Čas kliknutia na "Pridať do zbierky" |

---

## 3. Relačné väzby a kardinalita
- `users` (1) —— (N) `items` : Jeden používateľ vlastní viacero predmetov.
- `categories` (1) —— (N) `items` : Každý predmet patrí do jednej kategórie.
- `items` (1) —— (N) `price_history` : Každý predmet má časovú radu cenových záznamov.
- `users` (1) —— (N) `bot_filters` : Zberateľ môže mať definovaných viacero pravidiel sledovania.
- `bot_filters` (1) —— (N) `marketplace_listings` : Pravidlo generuje nájdené ponuky.
- `marketplace_listings` (1) —— (N) `notifications` : Z inzerátu vzniká interaktívna notifikácia.
- `notifications` (1) —— (0..1) `items` : Ak zberateľ klikne "Pridať", notifikácia sa transformuje na nový predmet v zbierke.
