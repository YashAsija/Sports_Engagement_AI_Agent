import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Sample historical sports knowledge base for vectorstore seeding
HISTORICAL_SPORTS_TRIVIA = [
    {
        "id": "cric_001",
        "sport": "Cricket",
        "title": "Virat Kohli 2023 World Cup Record",
        "content": "Virat Kohli scored 765 runs in the 2023 ICC Cricket World Cup, breaking Sachin Tendulkar's record for most runs in a single World Cup edition."
    },
    {
        "id": "cric_002",
        "sport": "Cricket",
        "title": "Fastest ODI Century",
        "content": "AB de Villiers holds the record for the fastest century in ODI cricket, scored in 31 balls against West Indies in Johannesburg in 2015."
    },
    {
        "id": "foot_001",
        "sport": "Football",
        "title": "Lionel Messi 91 Goals Record",
        "content": "Lionel Messi scored a record 91 goals in a single calendar year (2012) for FC Barcelona and Argentina."
    },
    {
        "id": "foot_002",
        "sport": "Football",
        "title": "Real Madrid Champions League Titles",
        "content": "Real Madrid won their 15th UEFA Champions League title in 2024, beating Borussia Dortmund 2-0 at Wembley Stadium."
    },
    {
        "id": "ten_001",
        "sport": "Tennis",
        "title": "Rafael Nadal French Open Record",
        "content": "Rafael Nadal has won 14 French Open (Roland Garros) singles titles, the most grand slam titles at a single tournament by any player."
    },
    {
        "id": "ten_002",
        "sport": "Tennis",
        "title": "Novak Djokovic Grand Slam Record",
        "content": "Novak Djokovic holds the record for the most Men's Singles Grand Slam titles with 24 major titles as of 2024."
    },
    {
        "id": "bask_001",
        "sport": "Basketball",
        "title": "LeBron James All-Time Scoring Record",
        "content": "LeBron James passed Kareem Abdul-Jabbar on February 7, 2023, to become the NBA's all-time leading scorer."
    },
    {
        "id": "bask_002",
        "sport": "Basketball",
        "title": "Wilt Chamberlain 100 Points",
        "content": "Wilt Chamberlain scored 100 points in a single NBA game on March 2, 1962, playing for the Philadelphia Warriors against the New York Knicks."
    },
    {
        "id": "f1_001",
        "sport": "Formula 1",
        "title": "Max Verstappen 19 Wins Season",
        "content": "Max Verstappen won 19 out of 22 races in the 2023 Formula 1 season with Red Bull Racing, setting the highest win percentage in F1 history."
    },
    {
        "id": "badm_001",
        "sport": "Badminton",
        "title": "Lin Dan Two-Time Olympic Gold",
        "content": "Lin Dan of China is the only men's singles badminton player to win back-to-back Olympic Gold medals (Beijing 2008 and London 2012)."
    }
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
            
            # Seed dataset if collection is empty
            if self.collection.count() == 0:
                self._seed_data()
        except Exception as e:
            logger.warning(f"ChromaDB initialization fallback mode active: {e}")
            self.collection = None

    def _seed_data(self):
        if not self.collection:
            return
        
        ids = [item["id"] for item in HISTORICAL_SPORTS_TRIVIA]
        documents = [item["content"] for item in HISTORICAL_SPORTS_TRIVIA]
        metadatas = [{"sport": item["sport"], "title": item["title"]} for item in HISTORICAL_SPORTS_TRIVIA]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query_facts(self, query: str, sport: Optional[str] = None, n_results: int = 2) -> Dict[str, Any]:
        """
        Query ChromaDB for relevant historical trivia.
        """
        if self.collection:
            try:
                where_clause = {"sport": sport} if sport else None
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_clause
                )
                
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                doc_ids = results.get("ids", [[]])[0]
                
                formatted_text = ""
                sources = []
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    doc_id = doc_ids[i] if i < len(doc_ids) else f"doc_{i}"
                    title = meta.get("title", f"Historical {sport} Record")
                    
                    formatted_text += f"Historical Record [{title}]: {doc}\n"
                    sources.append({
                        "source_type": "chromadb",
                        "citation_title": title,
                        "url_or_id": f"chroma://{doc_id}",
                        "snippet": doc
                    })
                    
                return {
                    "formatted_text": formatted_text,
                    "sources": sources
                }
            except Exception as e:
                logger.error(f"ChromaDB query error: {e}")
                
        # In-memory fallback if ChromaDB is unavailable
        filtered = [item for item in HISTORICAL_SPORTS_TRIVIA if not sport or item["sport"].lower() == sport.lower()]
        if not filtered:
            filtered = HISTORICAL_SPORTS_TRIVIA[:2]
        
        formatted_text = ""
        sources = []
        for item in filtered[:n_results]:
            formatted_text += f"Historical Record [{item['title']}]: {item['content']}\n"
            sources.append({
                "source_type": "chromadb",
                "citation_title": item['title'],
                "url_or_id": f"chroma://{item['id']}",
                "snippet": item['content']
            })
            
        return {
            "formatted_text": formatted_text,
            "sources": sources
        }

vector_store_instance = SportsVectorStore()
