"""
api_catalog.py - Katalógová a verejná API služba
Automatické dopĺňanie metadát a fotografií k predmetom.
Úplne eliminuje potrebu manuálneho vypisovania zberateľom.
"""

from typing import List, Dict, Any, Optional
import urllib.parse

CATALOG_DATABASE: List[Dict[str, Any]] = [
    # PlayStation
    {
        "name": "Sony PlayStation 2 Slim (Čierna, SCPH-70004)",
        "category": "Konzoly",
        "brand": "Sony Interactive Entertainment",
        "release_year": 2004,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 75.00,
        "photo_url": "https://images.unsplash.com/photo-1592840496073-e53bb3298ec5?w=600&auto=format&fit=crop&q=80",
        "description": "Najpredávanejšia herná konzola v histórii v kompaktnom Slim vyhotovení s DVD mechanikou."
    },
    {
        "name": "Sony PlayStation 3 Fat 60GB (Spätne kompatibilná)",
        "category": "Konzoly",
        "brand": "Sony Interactive Entertainment",
        "release_year": 2006,
        "default_condition": "Dobrý",
        "estimated_value": 140.00,
        "photo_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&auto=format&fit=crop&q=80",
        "description": "Pôvodná verzia PS3 s hardvérovým Emotion Engine čipom umožňujúcim natívne hranie PS2 hier."
    },
    {
        "name": "Sony PlayStation Portable (PSP-3000 Piano Black)",
        "category": "Konzoly",
        "brand": "Sony",
        "release_year": 2008,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 85.00,
        "photo_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80",
        "description": "Prenosná herná konzola s jasným LCD displejom, UMD mechanikou a Wi-Fi konektivitou."
    },

    # Apple iPod
    {
        "name": "Apple iPod Classic 6th Gen (80GB Silver)",
        "category": "Retro elektronika",
        "brand": "Apple",
        "release_year": 2007,
        "default_condition": "Výborný",
        "estimated_value": 120.00,
        "photo_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
        "description": "Kultový prehrávač s eloxovaným hliníkovým telom, mechanickým Click Wheel a kapacitou 80GB."
    },
    {
        "name": "Apple iPod Video 5.5th Gen (Wolfson DAC 30GB White)",
        "category": "Retro elektronika",
        "brand": "Apple",
        "release_year": 2006,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 135.00,
        "photo_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=600&auto=format&fit=crop&q=80",
        "description": "Audiofilmi najvyhľadávanejší iPod s legendárnym zvukovým prevodníkom Wolfson WM8758."
    },
    {
        "name": "Apple iPod Mini 2nd Gen (4GB Blue)",
        "category": "Retro elektronika",
        "brand": "Apple",
        "release_year": 2005,
        "default_condition": "Dobrý",
        "estimated_value": 45.00,
        "photo_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80",
        "description": "Kompaktný iPod s monochromatickým podsvieteným displejom a batériou s výdržou až 18 hodín."
    },

    # Nintendo
    {
        "name": "Nintendo Game Boy Color (Atomic Purple)",
        "category": "Konzoly",
        "brand": "Nintendo",
        "release_year": 1998,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 95.00,
        "photo_url": "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?w=600&auto=format&fit=crop&q=80",
        "description": "Prenosná 8-bitová konzola s farebným reflexným LCD displejom v priehľadnom fialovom šasi."
    },
    {
        "name": "Nintendo DS Lite (Polar White)",
        "category": "Konzoly",
        "brand": "Nintendo",
        "release_year": 2006,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 55.00,
        "photo_url": "https://images.unsplash.com/photo-1612287232202-a7e80f4f9f6e?w=600&auto=format&fit=crop&q=80",
        "description": "Dvojdisplejová konzola s dotykovým perom a slotom pre pôvodné Game Boy Advance kazety."
    },
    {
        "name": "Nintendo Switch OLED Model (Neon Red/Blue)",
        "category": "Konzoly",
        "brand": "Nintendo",
        "release_year": 2021,
        "default_condition": "Výborný",
        "estimated_value": 260.00,
        "photo_url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=600&auto=format&fit=crop&q=80",
        "description": "Hybridná konzola so žiarivým 7-palcovým OLED displejom a širokým nastaviteľným stojanom."
    },

    # Xbox
    {
        "name": "Microsoft Xbox 360 S (250GB Matte Black)",
        "category": "Konzoly",
        "brand": "Microsoft",
        "release_year": 2010,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 65.00,
        "photo_url": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=600&auto=format&fit=crop&q=80",
        "description": "Tichá a spoľahlivá verzia Xbox 360 s integrovanou Wi-Fi a bezdrôtovým ovládačom."
    },
    {
        "name": "Original Microsoft Xbox (Classic 2001)",
        "category": "Konzoly",
        "brand": "Microsoft",
        "release_year": 2001,
        "default_condition": "Dobrý",
        "estimated_value": 90.00,
        "photo_url": "https://images.unsplash.com/photo-1605901309584-818e25960a8f?w=600&auto=format&fit=crop&q=80",
        "description": "Prvá konzola od Microsoftu so vstavaným pevným diskom a procesorom Intel Pentium III."
    },

    # Fotoaparáty & Kamery
    {
        "name": "Sony Cyber-shot DSC-W80 Retro Digitál",
        "category": "Fotoaparáty",
        "brand": "Sony",
        "release_year": 2007,
        "default_condition": "Veľmi dobrý",
        "estimated_value": 60.00,
        "photo_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
        "description": "Kompaktný 7.2 megapixelový digitálny fotoaparát s optikou Carl Zeiss Vario-Tessar."
    },
    {
        "name": "Sony DCR-TRV250E Digital8 Handycam",
        "category": "Kamery",
        "brand": "Sony",
        "release_year": 2003,
        "default_condition": "Dobrý",
        "estimated_value": 110.00,
        "photo_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
        "description": "Kazetová videokamera s režimom nočného videnia NightShot Plus a optickým zoomom 20x."
    },
    {
        "name": "Fujifilm Instax Square SQ1 (Chalk White)",
        "category": "Fotoaparáty",
        "brand": "Fujifilm",
        "release_year": 2020,
        "default_condition": "Výborný",
        "estimated_value": 85.00,
        "photo_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&auto=format&fit=crop&q=80",
        "description": "Analógový fotoaparát na štvorcový instantný film s automatickou expozíciou."
    },

    # Zberateľské karty & Hračky
    {
        "name": "Pokemon Charizard 1st Edition Base Set (Shadowless)",
        "category": "Karty & Hry",
        "brand": "Wizards of the Coast",
        "release_year": 1999,
        "default_condition": "Near Mint",
        "estimated_value": 1450.00,
        "photo_url": "https://images.pokemontcg.io/base1/4_hires.png",
        "description": "Svätý grál zberateľstva Pokémon kariet – pôvodná holografická karta 4/102."
    },
    {
        "name": "LEGO Star Wars UCS Millennium Falcon (75192)",
        "category": "LEGO & Modely",
        "brand": "LEGO Group",
        "release_year": 2017,
        "default_condition": "Nové (Zapečatené)",
        "estimated_value": 850.00,
        "photo_url": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=600&auto=format&fit=crop&q=80",
        "description": "Jeden z najväčších LEGO modelov v histórii so 7 541 dielikmi a figúrkami posádky."
    }
]

ALIASES = {
    "ps2": ["playstation 2", "ps2", "sony playstation 2"],
    "ps3": ["playstation 3", "ps3", "sony playstation 3"],
    "ps4": ["playstation 4", "ps4"],
    "ps5": ["playstation 5", "ps5"],
    "psp": ["playstation portable", "psp"],
    "gba": ["game boy advance", "gameboy"],
    "gbc": ["game boy color", "gameboy"],
    "nds": ["nintendo ds"],
    "switch": ["nintendo switch"],
    "fotak": ["fotoaparat", "cyber-shot", "instax", "nikon", "canon"],
    "kamera": ["handycam", "videokamera", "digital8", "camcorder"]
}

def search_catalog_api(query: str) -> List[Dict[str, Any]]:
    """
    Vyhľadávanie vo verejnom katalógovom API s podporou bežných zberateľských skratiek
    a zoradením podľa najvyššej relevancie.
    """
    query_clean = query.strip().lower()
    if not query_clean:
        return CATALOG_DATABASE[:6]

    # Rozšírenie dopytu o aliasy
    expanded_terms = [query_clean]
    for key, alias_list in ALIASES.items():
        if key in query_clean:
            expanded_terms.extend(alias_list)

    scored_results = []
    for item in CATALOG_DATABASE:
        name_lower = item['name'].lower()
        full_text = f"{item['name']} {item['category']} {item['brand']}".lower()

        score = 0
        if query_clean in name_lower:
            score += 10
        for term in expanded_terms:
            if term in name_lower:
                score += 5
            elif term in full_text:
                score += 2

        if score > 0:
            scored_results.append((score, item))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored_results]

def get_item_enrichment(title: str) -> Optional[Dict[str, Any]]:
    """
    Pokúsi sa automaticky spárovať názov (napr. z inzerátu Vinted) s katalógom
    a vráti odporúčané metadáta a odhad trhovej ceny.
    """
    title_lower = title.lower()
    for item in CATALOG_DATABASE:
        # Skontrolujeme kľúčové slová položky
        keywords = item["name"].lower().split()
        if any(kw in title_lower for kw in ["ps2", "playstation 2"]) and "ps2" in item["name"].lower():
            return item
        if any(kw in title_lower for kw in ["ipod"]) and "ipod" in item["name"].lower():
            return item
        if any(kw in title_lower for kw in ["charizard"]) and "charizard" in item["name"].lower():
            return item
        if any(kw in title_lower for kw in ["game boy"]) and "game boy" in item["name"].lower():
            return item

    # Všeobecné vyhľadanie
    matches = search_catalog_api(title)
    if matches:
        return matches[0]

    return None
