@echo off
chcp 65001 >nul
echo ========================================================
echo     Inicializacia adresarovej struktury rocnikoveho projektu
echo     Metodika inspirovana RUP
echo ========================================================
echo.

set /p PROJ_NAME="Zadajte nazov projektu bez medzier a diakritiky: "

if "%PROJ_NAME%"=="" (
    echo Chyba: Nazov projektu nesmie byt prazdny!
    pause
    exit /b 1
)

echo.
echo Vytvaram projektovy priecinok: %PROJ_NAME%
mkdir "%PROJ_NAME%" 2>nul
mkdir "%PROJ_NAME%\01_Poziadavky" 2>nul
mkdir "%PROJ_NAME%\02_Analyza" 2>nul
mkdir "%PROJ_NAME%\03_Navrh" 2>nul
mkdir "%PROJ_NAME%\04_Implementacia" 2>nul
mkdir "%PROJ_NAME%\04_Implementacia\src" 2>nul
mkdir "%PROJ_NAME%\05_Testovanie" 2>nul
mkdir "%PROJ_NAME%\06_Dokumentacia" 2>nul

echo Vytvaram uvodny README.md...
(
echo # %PROJ_NAME%
echo.
echo ## Uvodny subor projektu
echo - **Nazov projektu:** %PROJ_NAME%
echo - **Autor:** [Meno a Priezvisko]
echo - **Trieda:** [Trieda]
echo - **Ciel projektu:** Jednotny nastroj pre zberatelov - sprava portfolia a monitorovaci bot.
echo.
echo ## Postup spustenia aplikacie
echo ```bash
echo python 04_Implementacia\src\main.py
echo ```
) > "%PROJ_NAME%\README.md"

echo.
echo ========================================================
echo  Adresarova struktura uspesne vytvorena!
echo  Naplnte svoje dokumenty do prislusnych priecinkov.
echo ========================================================
pause
