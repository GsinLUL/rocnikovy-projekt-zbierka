# Používateľský návod (User Manual)

Tento návod vysvetľuje prácu so systémom **Zbierka** z pohľadu koncového zberateľa.

---

## 1. Úvod a prihlásenie
Po otvorení aplikácie sa zberateľ prihlási svojím používateľským menom a heslom.  
Na úvodnej obrazovke (Dashboard) okamžite vidí:
- Celkovú odhadovanú hodnotu svojej zbierky,
- Celkovú investovanú sumu (kúpne ceny),
- Čistý zisk a percentuálne zhodnotenie (ROI),
- Interaktívny graf vývoja cien v čase.

---

## 2. Pridanie nového predmetu pomocou verejného API
Pre pridanie predmetu do zbierky:
1. Kliknite na tlačidlo **„+ Pridať predmet s API“**.
2. Do vyhľadávacieho poľa napíšte názov predmetu (napr. *„Charizard base set“*) alebo naskenujte čiarový kód.
3. Systém vyhľadá záznam vo verejnom katalógovom API.
4. Kliknite na **„Vybrať toto“**.
5. Systém automaticky predvyplní oficiálny názov, sériu, rok vydania, raritu a stiahne referenčnú fotografiu.
6. Vyberte fyzický stav vašej položky (napr. *Near Mint*) a zadajte cenu, za ktorú ste predmet kúpili.
7. Kliknite na **„Uložiť do zbierky“**.

---

## 3. Nastavenie autonómneho monitorovacieho bota
Pre automatické sledovanie výhodných ponúk na trhoviskách (Vinted):
1. V hornom menu zvoľte záložku **„Monitor bot“**.
2. Vyplňte **kľúčové slová** hľadaného predmetu (napr. *„Charizard Base Set holo“*).
3. Nastavte **maximálnu cenu** (strop), napríklad `150 €`. Všetky ponuky nad túto cenu bot automaticky odfiltruje.
4. Zvoľte **vylučovacie slová** (napr. *„reprint, proxy, obal“*), aby ste nedostávali falošné ponuky a obaly.
5. Zvoľte cieľové trhovisko (*Vinted*).
6. Kliknite na **„Aktivovať monitorovanie“**.
7. Bot teraz beží nepretržite na pozadí.

---

## 4. Reakcia na interaktívnu notifikáciu (Automatické pridanie)
Keď bot objaví inzerát vyhovujúci vašim kritériám:
1. Okamžite sa vám zobrazí **interaktívna notifikácia** s fotografiou, cenou a názvom ponuky.
2. Máte k dispozícii možnosti:
   - **Zobraziť na Vinted:** Otvorí inzerát priamo na webe/v aplikácii trhoviska pre kúpu.
   - **Ignorovať:** Zatvorí notifikáciu bez uloženia.
   - **★ PRIDAŤ DO ZBIERKY:** Jedným kliknutím zaeviduje položku do vašej databázy.
3. Po kliknutí na **„PRIDAŤ DO ZBIERKY“**:
   - Systém položku okamžite zapíše do vášho portfólia.
   - Systém v reálnom čase **prepočíta celkovú hodnotu vašej zbierky** a zobrazí vám aktualizovaný sumár.
