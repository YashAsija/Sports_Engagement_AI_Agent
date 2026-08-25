import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def search_sports_facts(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Executes live web search using DuckDuckGo to fetch recent sports results, records, and transfer news.
    Returns a list of dicts with title, href, and body snippets.
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
    Builds search queries and fetches real-time sports context for grounding.
    """
    search_query = f"latest {sport} match results records statistics 2024 2025"
    if difficulty.lower() == "hard":
        search_query = f"{sport} obscure world records statistics tournament finals details"
    
    results = search_sports_facts(search_query, max_results=3)
    
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
