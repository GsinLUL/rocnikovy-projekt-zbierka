"""
Služba pre integráciu verejných API a automatické dopĺňanie metadát a fotografií.
Eliminuje manuálne vypisovanie údajov zberateľom.
"""

from typing import Dict, Any, Optional

class PublicCatalogApiService:
    """
    Služba pre vyhľadávanie v katalógových verejných API (napr. PokéAPI, BGG, Discogs).
    Obsahuje katalógové záznamy a simuluje dopytovanie externého REST API.
    """

    MOCK_CATALOG = {
        "charizard base set": {
            "external_id": "pkmn-base-4",
            "name": "Charizard #4 Base Set (1st Edition / Shadowless)",
            "category": "Pokémon TCG",
            "release_year": 1999,
            "publisher": "Wizards of the Coast",
            "rarity": "Holo Rare",
            "photo_url": "https://images.pokemontcg.io/base1/4_hires.png",
            "recommended_market_price": 1250.00,
            "description": "Legendárna holografická karta Charizard z pôvodnej základnej série z roku 1999."
        },
        "black lotus": {
            "external_id": "mtg-unl-bl",
            "name": "Black Lotus (Unlimited Edition)",
            "category": "Magic: The Gathering",
            "release_year": 1993,
            "publisher": "Wizards of the Coast",
            "rarity": "Rare",
            "photo_url": "https://cards.scryfall.io/large/front/b/d/bd8fa327.jpg",
            "recommended_market_price": 4500.00,
            "description": "Najcennejšia a najznámejšia karta z Magic: The Gathering Power Nine."
        },
        "lego ucs millennium falcon": {
            "external_id": "lego-75192",
            "name": "LEGO Star Wars UCS Millennium Falcon (75192)",
            "category": "LEGO Star Wars",
            "release_year": 2017,
            "publisher": "LEGO Group",
            "rarity": "Ultimate Collector Series",
            "photo_url": "https://www.lego.com/cdn/cs/set/assets/blt022137/75192.jpg",
            "recommended_market_price": 849.99,
            "description": "Monumentálny zberateľský model Millenium Falcon obsahujúci 7 541 dielikov."
        }
    }

    def search_item(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Vyhľadá položku vo verejnom API podľa zadaného reťazca.
        """
        query_norm = query.strip().lower()
        # Priama zhoda alebo vyhľadanie podľa kľúčového slova
        for key, data in self.MOCK_CATALOG.items():
            if query_norm in key or key in query_norm:
                return data
        return None

    def enrich_item_data(self, query: str) -> Dict[str, Any]:
        """
        Obohatí dáta položky z verejného API. Ak položku nenájde, vráti základnú štruktúru pre manuálne zadanie.
        """
        found = self.search_item(query)
        if found:
            return {
                "success": True,
                "data": found,
                "message": f"Dáta a fotografia pre '{found['name']}' úspešne stiahnuté z verejného API."
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": f"Pre dotaz '{query}' sa vo verejnom API nenašli žiadne oficiálne záznamy. Prepínam na manuálny režim."
            }
