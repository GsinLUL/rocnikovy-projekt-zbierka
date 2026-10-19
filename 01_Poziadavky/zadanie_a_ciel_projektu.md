# Zadanie a cieľ projektu

## Názov projektu
**Zberateľský portál a monitorovací systém (Zbierka)**  
*Integrovaná správa zberateľského portfólia s autonómnym botom pre sledovanie online trhovísk*

---

## 1. Motivácia a kontext
Zberateľstvo (napr. zberateľské kartové hry ako Pokémon, Magic: The Gathering, športové kartičky, numizmatika, lego sety, vinylové platne, či vintage móda) sa v posledných rokoch stalo nielen populárnym hobby, ale aj alternatívnou investičnou triedou s rýchlo sa meniacimi trhovými cenami.

Zberatelia dnes čelia dvom hlavným problémom:
1. **Zdĺhavá a neefektívna manuálna evidencia:** Zberatelia musia často ručne prepisovať názvy, čísla sérií, parametre a hľadať či fotiť referenčné obrázky pre desiatky až stovky predmetov.
2. **Nestíhanie výhodných ponúk na sekundárnych trhoch:** Na platformách ako Vinted, Bazoš či eBay sa výhodné inzeráty (pod trhovou cenou) vypredajú často v priebehu niekoľkých minút od zverejnenia. Manuálne neustále obnovovanie vyhľadávania je časovo neudržateľné.
3. **Absencia prepojenia medzi nákupom a portfóliom:** Keď zberateľ nájde alebo kúpi predmet, musí ho opätovne manuálne zaevidovať do svojej tabuľky a prepočítať celkovú hodnotu zbierky.

---

## 2. Hlavný cieľ projektu
Cieľom projektu je navrhnúť, analyzovať a implementovať **jednotný, plne integrovaný softvérový systém pre zberateľov**, ktorý spája:
- **Centrálnu databázovú aplikáciu** (s responzívnym webovým aj mobilným rozhraním) pre správu osobného portfólia zberateľa, automatické obohacovanie dát z verejných API a sledovanie trhovej hodnoty v čase.
- **Autonómneho monitorovacieho agenta (bota)**, ktorý nepretržite skenuje sekundárne trhoviská (primárne Vinted) podľa zadaných filtrov a cenových limitov a okamžite odosiela interaktívne notifikácie.
- **Kľúčové prepojenie oboch modulov:** Používateľ dokáže priamo z notifikácie jedným kliknutím zaevidovať nájdený predmet do databázy, pričom systém okamžite prepočíta celkovú hodnotu jeho zbierky.

---

## 3. Rozsah projektu (Scope)
Projekt pozostáva z dvoch úzko prepojených modulov:

### Modul A: Databázová aplikácia pre správu portfólia (Web & Mobil)
- Evidencia zberateľských predmetov s ich fyzickým stavom, kúpnou cenou, dátumom nadobudnutia a poznámkami.
- **Integrácia verejných API:** Automatické načítanie oficiálnych metadát, fotografií, popisu a technických parametrov položky bez nutnosti manuálneho vypisovania.
- **Analytika trhových cien:** Sledovanie vývoja trhových cien položiek v čase, vizualizácia historických grafov a automatický výpočet zhodnotenia (ROI).

### Modul B: Autonómny monitorovací skript (Bot)
- Nepretržité, autonómne skenovanie online trhovísk (napr. Vinted).
- Filtrovanie ponúk na základe kľúčových slov, kategórií, maximálnej ceny a negatívnych vylučovacích slov.
- Generovanie **interaktívnych notifikácií** (názov, cena, fotografia, odkaz a akčné tlačidlo pre rýchle pridanie).

### Kľúčový integrujúci prvok:
- **Automatické pridávanie (Quick Add):** Po úspešnej interakcii s interaktívnou notifikáciou sa daný predmet priamo zapíše do používateľovej databázy a okamžite sa prepočíta celková hodnota jeho zbierky.
