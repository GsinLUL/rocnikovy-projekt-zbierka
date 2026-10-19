#!/bin/bash
# Inicializácia adresárovej štruktúry ročníkového projektu (macOS / Linux)
# Metodika inšpirovaná RUP

echo "========================================================"
echo "    Inicializácia adresárovej štruktúry ročníkového projektu"
echo "    Metodika inšpirovaná RUP"
echo "========================================================"
echo ""

read -p "Zadajte názov projektu bez medzier a diakritiky: " PROJ_NAME

if [ -z "$PROJ_NAME" ]; then
    echo "Chyba: Názov projektu nesmie byť prázdny!"
    exit 1
fi

echo ""
echo "Vytváram projektový priečinok: $PROJ_NAME"
mkdir -p "$PROJ_NAME/01_Poziadavky"
mkdir -p "$PROJ_NAME/02_Analyza"
mkdir -p "$PROJ_NAME/03_Navrh"
mkdir -p "$PROJ_NAME/04_Implementacia/src"
mkdir -p "$PROJ_NAME/05_Testovanie"
mkdir -p "$PROJ_NAME/06_Dokumentacia"

cat << EOF > "$PROJ_NAME/README.md"
# $PROJ_NAME

## Úvodný súbor projektu
- **Názov projektu:** $PROJ_NAME
- **Autor:** Maxim
- **Trieda:** 3. ročník
- **Cieľ projektu:** Jednotný nástroj pre zberateľov spájajúci databázové portfólio s autonómnym botom.

## Postup spustenia aplikácie
\`\`\`bash
python3 04_Implementacia/src/main.py
\`\`\`
EOF

chmod +x "$PROJ_NAME/04_Implementacia/src/main.py" 2>/dev/null

echo "========================================================"
echo " Adresárová štruktúra úspešne vytvorená!"
echo "========================================================"
