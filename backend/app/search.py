import logging
import datetime
import random
from typing import List, Dict, Any
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# State tracking for query angle rotation
LAST_QUERY_ANGLES = {}

QUERY_ANGLES = {
    "cricket": [
        "world cup records 2024 2025",
        "highest individual scores history",
        "player milestones recent",
        "ICC rankings current",
        "test match records",
        "ODI statistics",
        "T20 world records",
        "recent match results 2024 2025"
    ],
    "football": [
        "transfer news 2024 2025",
        "Champions League records",
        "top scorers all time",
        "World Cup history facts",
        "Ballon d'Or winners",
        "recent match results 2024 2025"
    ],
    "tennis": [
        "Grand Slam titles singles records",
        "ATP WTA rankings current 2024 2025",
        "Wimbledon US Open winners recent",
        "fastest serves history records"
    ],
    "basketball": [
        "NBA finals champions 2024 2025",
        "all time scoring leaders NBA",
        "three point records NBA",
        "recent game stats 2024 2025"
    ],
    "badminton": [
        "Olympic gold medals badminton winners",
        "BWF world championships stats",
        "fastest badminton smashes history",
        "Thomas Cup All England winners"
    ]
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

def get_live_sports_context(sport: str, difficulty: str = "Medium") -> Dict[str, Any]:
    """
    Builds timestamp-based, rotated query angles prepended with sport name and site-specific targets.
    """
    sport_clean = sport.lower().strip()
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime("%B %Y")
    
    # 1. Rotate query angle
    angles = QUERY_ANGLES.get(sport_clean, [f"records and news {current_year}", f"statistics and milestones {current_year}"])
    last_idx = LAST_QUERY_ANGLES.get(sport_clean, -1)
    next_idx = (last_idx + 1) % len(angles)
    LAST_QUERY_ANGLES[sport_clean] = next_idx
    angle = angles[next_idx]

    # 2. Site-specific reliable sources query
    site_filter = "site:espncricinfo.com OR site:bbc.com/sport OR site:fifa.com OR site:atptour.com OR site:nba.com"
    search_query = f"{sport} {angle} {current_month} {site_filter}"

    results = search_sports_facts(search_query, max_results=4)
    
    formatted_context = ""
    sources = []
    for idx, item in enumerate(results, 1):
        formatted_context += f"Source [{idx}] ({item['title']}): {item['snippet']}\n"
        sources.append({
            "source_type": "web_search",
            "citation_title": item["title"],
            "url_or_id": item["url"],
            "snippet": item["snippet"][:150] + "..." if len(item["snippet"]) > 150 else item["snippet"]
        })
        
    return {
        "formatted_text": formatted_context,
        "sources": sources
    }
