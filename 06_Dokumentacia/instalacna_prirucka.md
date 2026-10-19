# Inštalačná príručka a postup spustenia (Installation Guide)

Tento návod slúži pre hodnotiteľa / učiteľa a koncového používateľa na **samostatné a bezproblémové spustenie projektu**.

---

## 1. Požiadavky na softvér a systém
- **Operačný systém:** Windows 10/11, macOS (Ventura, Sonoma, Sequoia) alebo Linux (Ubuntu 20.04+)
- **Programovací jazyk:** Python 3.9 alebo novší (odporúčaný Python 3.10 / 3.11 / 3.12)
- **Knižnice:** Základný demonštračný prototyp využíva štandardnú knižnicu Pythonu (`dataclasses`, `unittest`, `datetime`, `json`, `zipfile`, `xml`), vďaka čomu **nevyžaduje žiadne externé pip inštalácie pre overenie funkčnosti!**
- **Voliteľné pre plnú verziu:** `pip install -r 04_Implementacia/requirements.txt`

---

## 2. Klonovanie / Otvorenie projektu
Otvorte terminál (alebo príkazový riadok CMD / PowerShell) a prejdite do koreňového priečinka projektu:
```bash
cd "/cesta/k/projektu/zbierka"
```

---

## 3. Rýchle spustenie demonštračnej aplikácie
Aplikácia obsahuje plne funkčný skript integrujúci obidva kľúčové moduly (databázové portfólio + autonómny bot + interaktívna notifikácia + okamžitý prepočet):

```bash
# Na macOS / Linux:
python3 04_Implementacia/src/main.py

# Na Windows:
python 04_Implementacia\src\main.py
```

### Čo skript vykoná:
1. Zobrazí používateľský profil a počiatočný stav zberateľskej zbierky (kúpnu cenu a celkovú trhovú hodnotu).
2. Vykoná dopyt na verejné API pre zberateľskú kartu (automaticky doplní metadáta a fotografiu).
3. Spustí autonómneho monitorovacieho bota s používateľskými filtrami.
4. Bot prefiltruje ponuky z online trhoviska Vinted a zachytí výhodný inzerát.
5. Vygeneruje interaktívnu notifikáciu s akciou pridania.
6. Vykoná interakciu „Pridať do zbierky“: zapíše položku do databázy a **v reálnom čase prepočíta celkovú hodnotu zbierky**, pričom zobrazí porovnávaciu tabuľku PRED a PO pridaní.

---

## 4. Spustenie automatizovaných testov
Pre overenie správnosti funkčnej logiky a akceptačných kritérií spustite unit testy:

```bash
# Na macOS / Linux:
python3 05_Testovanie/test_portfolio.py

# Na Windows:
python 05_Testovanie\test_portfolio.py
```

Výstup by mal hlásiť:
```
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

---

## 5. Prihlasovacie roly pre testovanie
V súlade s bezpečnostnými zásadami (neukladať do projektu heslá) sú v systéme definované tieto testovacie roly:
- **Zberateľ (Bežný používateľ):** `zberatel_peter` (prístup k svojmu portfóliu, nastaveniam botov a notifikáciám)
- **Administrátor:** `admin` (prístup k systémovému monitoringu, API kľúčom a správcom workerov)
