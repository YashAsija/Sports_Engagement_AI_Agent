import logging
import datetime
import random
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from backend.app.vectorstore import format_source

logger = logging.getLogger(__name__)

# Bug 3: Sport-specific query angles
QUERY_ANGLES = {
    'cricket': [
        '{sport} batting world records centuries',
        '{sport} bowling wickets records history',  
        '{sport} World Cup champions winners years',
        '{sport} player career milestones 2024 2025',
        '{sport} ICC tournaments T20 ODI Test facts',
    ],
    'football': [
        '{sport} goal scoring records all time',
        '{sport} World Cup history winners nations',
        '{sport} Champions League records titles',
        '{sport} player awards career statistics',
        '{sport} recent results transfers 2024 2025',
    ],
    'tennis': [
        '{sport} Grand Slam records titles history',
        '{sport} serve speed records ATP WTA',
        '{sport} Wimbledon French Open US Open facts',
        '{sport} player career retirement milestones',
        '{sport} recent tournament results 2024 2025',
    ],
    'basketball': [
        '{sport} NBA scoring records history',
        '{sport} championship winners history',
        '{sport} player stats points rebounds assists',
        '{sport} three point records rules facts',
        '{sport} recent season draft results 2024',
    ],
    'badminton': [
        '{sport} world championship records',
        '{sport} Olympic medal history winners',
        '{sport} smash speed records BWF',
        '{sport} Thomas Cup Uber Cup history',
        '{sport} recent tournament results 2024 2025',
    ],
    'formula1': [
        '{sport} world championship titles records',
        '{sport} race wins constructor history',
        '{sport} fastest lap speed records Monza',
        '{sport} driver career facts history legends',
        '{sport} recent race results season 2024 2025',
    ],
}

def search_sports_facts(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Executes live web search using DuckDuckGo to fetch recent sports results, records, and transfer news.
    """
    try:
        results = []
        with DDGS() as ddgs:
            ddg_gen = ddgs.text(query, max_results=max_results)
            for r in ddg_gen:
                results.append({
                    "title": r.get("title", "Sports News Result"),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search error: {e}. Falling back to default search context.")
        return [
            {
                "title": f"Recent {query} Information",
                "url": "https://www.espn.com/sports",
                "snippet": f"Latest tournament records, match stats, and official team updates regarding {query}."
            }
        ]

def get_live_sports_context(sport: str, difficulty: str = "Medium", custom_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Builds search context using sport-specific query angles.
    """
    sport_clean = sport.lower().strip().replace(" ", "")
    current_year = datetime.datetime.now().year
    
    if custom_query:
        search_query = custom_query
    else:
        angles = QUERY_ANGLES.get(sport_clean, [f"{sport} records history statistics facts"])
        search_query = angles[0].replace('{sport}', sport)

    results = search_sports_facts(search_query, max_results=4)
    
    formatted_context = ""
    sources = []
    for idx, item in enumerate(results, 1):
        formatted_context += f"Source [{idx}] ({item['title']}): {item['snippet']}\n"
        src_dict = format_source(item["url"], sport)
        sources.append({
            "source_type": "web_search",
            "citation_title": item["title"],
            "url_or_id": item["url"],
            "display_source": src_dict["label"],
            "source_obj": src_dict,
            "snippet": item["snippet"][:150] + "..." if len(item["snippet"]) > 150 else item["snippet"]
        })
        
    return {
        "formatted_text": formatted_context,
        "sources": sources
    }
