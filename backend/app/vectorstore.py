import hashlib
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def format_source(source: str, sport: str) -> Dict[str, Any]:
    """
    Formats source URL or chroma UUID into human-readable dict label and URL for frontend.
    """
    sport_icons = {
        'cricket': '🏏', 'football': '⚽', 'tennis': '🎾',
        'basketball': '🏀', 'badminton': '🏸', 'formula1': '🏎️', 'formula 1': '🏎️'
    }
    icon = sport_icons.get(sport.lower(), '🏆')
    
    if not source or 'chroma://' in source:
        return {
            'label': f'📚 {sport.capitalize()} Knowledge Base',
            'url': None,
            'type': 'chromadb'
        }
    domain_labels = {
        'espncricinfo': '🏏 ESPNcricinfo',
        'wikipedia': '📖 Wikipedia',
        'formula1.com': '🏎️ Formula1.com',
        'atptour': '🎾 ATP Tour',
        'fifa.com': '⚽ FIFA',
        'nba.com': '🏀 NBA',
        'bbc.com/sport': '📺 BBC Sport',
    }
    for key, label in domain_labels.items():
        if key in source.lower():
            return {'label': label, 'url': source, 'type': 'web'}
    
    try:
        domain = source.replace('https://','').replace('http://','').split('/')[0]
        return {'label': f'🌐 {domain}', 'url': source, 'type': 'web'}
    except Exception:
        return {'label': '🌐 Web Source', 'url': source, 'type': 'web'}

# Expanded Comprehensive Historical Sports Knowledge Base
HISTORICAL_SPORTS_TRIVIA = [
    # CRICKET
    {"fact": "Sachin Tendulkar scored 100 international centuries — 51 in Tests and 49 in ODIs.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "The highest individual score in Test cricket is 400 not out by Brian Lara against England in 2004.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "Virat Kohli scored 765 runs in the 2023 ODI World Cup, the most by any player in a single World Cup edition.", "sport": "cricket", "category": "records", "difficulty": "medium"},
    {"fact": "India won the 2024 T20 World Cup, defeating South Africa in the final by 7 runs.", "sport": "cricket", "category": "recent", "difficulty": "easy"},
    {"fact": "Jasprit Bumrah was named Player of the Tournament at the 2024 T20 World Cup.", "sport": "cricket", "category": "recent", "difficulty": "medium"},
    {"fact": "The fastest century in ODI cricket was scored by AB de Villiers in 31 balls against West Indies in 2015.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "Muthiah Muralidaran took 800 Test wickets, the most in Test cricket history.", "sport": "cricket", "category": "records", "difficulty": "medium"},
    {"fact": "Shane Warne took 708 Test wickets, the second most in history.", "sport": "cricket", "category": "records", "difficulty": "medium"},
    {"fact": "The first Cricket World Cup was held in 1975 in England, won by West Indies.", "sport": "cricket", "category": "history", "difficulty": "easy"},
    {"fact": "MS Dhoni is the only captain to win all three ICC trophies: World Cup 2011, World T20 2007, and Champions Trophy 2013.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "Rohit Sharma holds the record for highest individual score in ODIs — 264 against Sri Lanka in 2014.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "The Ashes is the Test series played between England and Australia, contested since 1882.", "sport": "cricket", "category": "history", "difficulty": "easy"},
    {"fact": "In T20 cricket, the maximum number of overs per team is 20.", "sport": "cricket", "category": "rules", "difficulty": "easy"},
    {"fact": "A cricket team has 11 players on the field.", "sport": "cricket", "category": "rules", "difficulty": "easy"},
    {"fact": "Rishabh Pant is the highest-scoring wicketkeeper-batsman in Test cricket history.", "sport": "cricket", "category": "records", "difficulty": "hard"},
    {"fact": "Rohit Sharma has hit the most sixes in T20 internationals.", "sport": "cricket", "category": "records", "difficulty": "medium"},
    {"fact": "The DRS (Decision Review System) uses ball-tracking technology called Hawk-Eye.", "sport": "cricket", "category": "rules", "difficulty": "medium"},
    {"fact": "Lasith Malinga took 4 wickets in 4 consecutive balls in ODI cricket.", "sport": "cricket", "category": "records", "difficulty": "hard"},

    # FOOTBALL
    {"fact": "Cristiano Ronaldo has scored over 900 senior career goals across club and international football.", "sport": "football", "category": "records", "difficulty": "easy"},
    {"fact": "Argentina won the 2022 FIFA World Cup in Qatar, defeating France in the final on penalties.", "sport": "football", "category": "recent", "difficulty": "easy"},
    {"fact": "Lionel Messi won the 2022 World Cup Golden Ball award.", "sport": "football", "category": "recent", "difficulty": "easy"},
    {"fact": "The UEFA Champions League was previously known as the European Cup before 1992.", "sport": "football", "category": "history", "difficulty": "medium"},
    {"fact": "Real Madrid has won the most UEFA Champions League titles — 15 as of 2024.", "sport": "football", "category": "records", "difficulty": "medium"},
    {"fact": "The fastest goal in World Cup history was scored by Hakan Şükür of Turkey in 11 seconds in 2002.", "sport": "football", "category": "records", "difficulty": "hard"},
    {"fact": "Gerd Muller scored 14 World Cup goals, a record that stood for 32 years before Ronaldo equalled it.", "sport": "football", "category": "records", "difficulty": "hard"},
    {"fact": "A standard football match lasts 90 minutes, divided into two halves of 45 minutes.", "sport": "football", "category": "rules", "difficulty": "easy"},
    {"fact": "Brazil has won the FIFA World Cup the most times — 5 times (1958, 1962, 1970, 1994, 2002).", "sport": "football", "category": "history", "difficulty": "medium"},
    {"fact": "Lamine Yamal scored in the Euro 2024 semi-final at age 16, becoming the youngest scorer in Euros history.", "sport": "football", "category": "recent", "difficulty": "hard"},
    {"fact": "Spain won Euro 2024, defeating England 2-1 in the final.", "sport": "football", "category": "recent", "difficulty": "easy"},
    {"fact": "The offside rule in football means an attacking player must have at least one opponent between them and the goal line when the ball is played.", "sport": "football", "category": "rules", "difficulty": "medium"},
    {"fact": "Pele scored 77 goals for Brazil, a record for the national team for decades.", "sport": "football", "category": "records", "difficulty": "medium"},
    {"fact": "The FIFA World Cup is held every 4 years.", "sport": "football", "category": "rules", "difficulty": "easy"},
    {"fact": "Manchester City won the Premier League in 2023-24 season, their fourth consecutive title.", "sport": "football", "category": "recent", "difficulty": "medium"},

    # TENNIS
    {"fact": "Novak Djokovic has won 24 Grand Slam singles titles, the most in tennis history.", "sport": "tennis", "category": "records", "difficulty": "easy"},
    {"fact": "Jannik Sinner won the 2024 Australian Open and US Open, finishing the year as World No. 1.", "sport": "tennis", "category": "recent", "difficulty": "medium"},
    {"fact": "Carlos Alcaraz won Wimbledon 2024 by defeating Novak Djokovic in the final.", "sport": "tennis", "category": "recent", "difficulty": "medium"},
    {"fact": "The four Grand Slams are Australian Open, French Open, Wimbledon, and US Open.", "sport": "tennis", "category": "rules", "difficulty": "easy"},
    {"fact": "Rafael Nadal has won the French Open 14 times, an all-time record at a single Grand Slam.", "sport": "tennis", "category": "records", "difficulty": "hard"},
    {"fact": "Serena Williams won 23 Grand Slam singles titles, the most by any player in the Open Era.", "sport": "tennis", "category": "records", "difficulty": "medium"},
    {"fact": "Wimbledon is the oldest tennis Grand Slam, first held in 1877.", "sport": "tennis", "category": "history", "difficulty": "medium"},
    {"fact": "In tennis, a score of 40-40 is called Deuce.", "sport": "tennis", "category": "rules", "difficulty": "easy"},
    {"fact": "Roger Federer retired from professional tennis in September 2022.", "sport": "tennis", "category": "recent", "difficulty": "easy"},
    {"fact": "The fastest serve ever recorded in ATP tennis was 263.4 km/h by Sam Groth in 2012.", "sport": "tennis", "category": "records", "difficulty": "hard"},

    # BASKETBALL
    {"fact": "LeBron James is the all-time leading scorer in NBA history with over 40,000 points.", "sport": "basketball", "category": "records", "difficulty": "easy"},
    {"fact": "The Boston Celtics won the 2024 NBA Championship, defeating the Dallas Mavericks 4-1.", "sport": "basketball", "category": "recent", "difficulty": "medium"},
    {"fact": "Michael Jordan won 6 NBA championships with the Chicago Bulls.", "sport": "basketball", "category": "history", "difficulty": "easy"},
    {"fact": "An NBA basketball game consists of four 12-minute quarters.", "sport": "basketball", "category": "rules", "difficulty": "easy"},
    {"fact": "Wilt Chamberlain scored 100 points in a single NBA game in 1962, a record that still stands.", "sport": "basketball", "category": "records", "difficulty": "hard"},
    {"fact": "The three-point line was introduced in the NBA in the 1979-80 season.", "sport": "basketball", "category": "history", "difficulty": "medium"},
    {"fact": "Stephen Curry holds the record for most three-pointers made in NBA history.", "sport": "basketball", "category": "records", "difficulty": "medium"},
    {"fact": "The NBA was founded in 1946 as the Basketball Association of America.", "sport": "basketball", "category": "history", "difficulty": "hard"},

    # BADMINTON
    {"fact": "PV Sindhu became the first Indian woman to win two Olympic medals in badminton (2016 silver, 2020 bronze).", "sport": "badminton", "category": "records", "difficulty": "medium"},
    {"fact": "Viktor Axelsen of Denmark won the men's singles gold at the 2020 Tokyo Olympics and 2024 Paris Olympics.", "sport": "badminton", "category": "recent", "difficulty": "hard"},
    {"fact": "An Seyoung of South Korea won the women's singles gold at the 2024 Paris Olympics.", "sport": "badminton", "category": "recent", "difficulty": "hard"},
    {"fact": "A badminton game is played to 21 points, and a player must win by 2 clear points.", "sport": "badminton", "category": "rules", "difficulty": "easy"},
    {"fact": "The fastest badminton smash ever recorded was 565 km/h by Mads Pieler Kolding in 2017.", "sport": "badminton", "category": "records", "difficulty": "hard"},
    {"fact": "Lin Dan of China has won the most BWF World Championship titles — 5 times.", "sport": "badminton", "category": "records", "difficulty": "hard"},
    {"fact": "The Thomas Cup is the most prestigious team event in men's badminton.", "sport": "badminton", "category": "history", "difficulty": "medium"},
    {"fact": "Badminton became an Olympic sport in 1992 at the Barcelona Olympics.", "sport": "badminton", "category": "history", "difficulty": "medium"},
    {"fact": "A shuttlecock has 16 feathers in a standard competition-grade birdie.", "sport": "badminton", "category": "rules", "difficulty": "hard"},
]

class SportsVectorStore:
    def __init__(self, collection_name: str = "sports_historical_facts"):
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            self._seed_data()
        except Exception as e:
            logger.warning(f"ChromaDB initialization fallback mode active: {e}")
            self.collection = None

    def _seed_data(self):
        if not self.collection:
            return
        
        # Bug 4 Fix: Metadata strictly added with {"sport": sport_name.lower()} and MD5 hash IDs
        ids = [hashlib.md5(item["fact"].encode('utf-8')).hexdigest() for item in HISTORICAL_SPORTS_TRIVIA]
        documents = [item["fact"] for item in HISTORICAL_SPORTS_TRIVIA]
        metadatas = [
            {
                "sport": item["sport"].lower(),
                "category": item["category"],
                "difficulty": item["difficulty"]
            }
            for item in HISTORICAL_SPORTS_TRIVIA
        ]
        
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_facts(self, query: str, sport: Optional[str] = None, n_results: int = 5) -> Dict[str, Any]:
        """
        Query ChromaDB for relevant historical trivia filtered strictly by sport metadata ($eq match).
        """
        sport_clean = sport.lower().strip() if sport else None

        if self.collection:
            try:
                # Bug 4 Fix: Exact sport metadata filter matching
                where_clause = {"sport": {"$eq": sport_clean}} if sport_clean else None
                results = self.collection.query(
                    query_texts=[f"{sport_clean or 'sports'} {query}"],
                    n_results=n_results,
                    where=where_clause
                )
                
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                doc_ids = results.get("ids", [[]])[0]
                
                formatted_text = ""
                sources = []
                for i, doc in enumerate(docs):
                    doc_id = doc_ids[i] if i < len(doc_ids) else f"doc_{i}"
                    raw_url = f"chroma://{doc_id}"
                    src_dict = format_source(raw_url, sport_clean or "Sports")
                    
                    formatted_text += f"Historical Record: {doc}\n"
                    sources.append({
                        "source_type": "chromadb",
                        "citation_title": src_dict['label'],
                        "url_or_id": raw_url,
                        "display_source": src_dict['label'],
                        "source_obj": src_dict,
                        "snippet": doc
                    })
                    
                return {
                    "formatted_text": formatted_text,
                    "sources": sources
                }
            except Exception as e:
                logger.error(f"ChromaDB query error: {e}")
                
        # In-memory fallback if ChromaDB query fails
        filtered = [item for item in HISTORICAL_SPORTS_TRIVIA if not sport_clean or item["sport"].lower() == sport_clean]
        if not filtered:
            filtered = HISTORICAL_SPORTS_TRIVIA[:2]
        
        formatted_text = ""
        sources = []
        for item in filtered[:n_results]:
            formatted_text += f"Historical Record: {item['fact']}\n"
            raw_url = f"chroma://{item['sport']}_{hashlib.md5(item['fact'].encode('utf-8')).hexdigest()[:6]}"
            src_dict = format_source(raw_url, item['sport'])
            sources.append({
                "source_type": "chromadb",
                "citation_title": src_dict['label'],
                "url_or_id": raw_url,
                "display_source": src_dict['label'],
                "source_obj": src_dict,
                "snippet": item['fact']
            })
            
        return {
            "formatted_text": formatted_text,
            "sources": sources
        }

vector_store_instance = SportsVectorStore()
