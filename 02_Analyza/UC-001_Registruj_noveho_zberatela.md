# Prípad použitia: UC-001 – Registruj a prihlás zberateľa

## Identifikátor:
`UC-001`

------------------------------------------------------------
## Názov:
**Registruj a prihlás zberateľa**

------------------------------------------------------------
## Popis:
Používateľ si vytvorí nové zberateľské konto v aplikácii, zvolí si preferovanú menu a prihlási sa do systému pre správu svojej zbierky.

------------------------------------------------------------
## Aktéri:
- **Primárny aktér:** Neregistrovaný návštevník / Zberateľ
- **Sekundárny aktér:** E-mailová notifikačná služba

------------------------------------------------------------
## Vstupné podmienky:
- Používateľ má otvorené webové alebo mobilné rozhranie aplikácie.
- Používateľ ešte nemá existujúce konto s rovnakou e-mailovou adresou.

------------------------------------------------------------
## Výstupné podmienky:
- V databáze je vytvorený nový používateľský účet s bezpečne zahashovaným heslom.
- Používateľovi je inicializované prázdne zberateľské portfólio.
- Používateľ je autentifikovaný a prihlásený v systéme.

------------------------------------------------------------
## Spúšťač (Trigger):
Používateľ klikne na tlačidlo „Zaregistrovať sa“ na úvodnej prihlasovacej obrazovke.

------------------------------------------------------------
## Hlavný scenár:
1. Používateľ vyplní registračný formulár: prihlasovacie meno, platný e-mail, heslo a potvrdí predvolenú menu (EUR/USD).
2. Používateľ odošle registračný formulár kliknutím na „Vytvoriť účet“.
3. Systém validuje správnosť formátu údajov a skontroluje unikátnosť e-mailovej adresy v databáze.
4. Systém bezpečne zašifruje heslo (pomocou bcrypt/Argon2) a zapíše nový používateľský záznam do databázy.
5. Systém inicializuje pre používateľa prázdnu zbierku a predvolené notifikačné preferencie.
6. Systém vygeneruje uvítací e-mail a automaticky prihlási používateľa do zberateľského dashboardu.

------------------------------------------------------------
## Alternatívne scenáre:
**3a – E-mailová adresa už v systéme existuje**
3a.1 Systém zobrazí chybovú správu: „Používateľ so zadaným e-mailom už existuje.“
3a.2 Systém ponúkne možnosť prechodu na obnovu hesla.
3a.3 Use case sa ukončí bez vytvorenia účtu.
**3b – Zadané heslo nespĺňa bezpečnostné kritériá**
3b.1 Systém zobrazí upozornenie o nedostatočnej sile hesla (vyžaduje sa min. 8 znakov, číslo a veľké písmeno).
3b.2 Používateľ je vyzvaný na opravu hesla (návrat ku kroku 1).
