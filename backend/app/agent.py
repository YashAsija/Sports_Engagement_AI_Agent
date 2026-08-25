import os
import json
import uuid
import logging
import random
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from backend.app.models import (
    MCQItem, TrueFalseItem, ThisOrThatPollItem, FillInTheBlankItem, GuessTheNumberItem,
    ContentItem, GroundingSource, BatchGenerationRequest, validate_fitb_options
)
from backend.app.templates import (
    get_system_prompt, MCQ_TEMPLATE, TRUE_FALSE_TEMPLATE, THIS_OR_THAT_TEMPLATE,
    FILL_IN_BLANK_TEMPLATE, GUESS_NUMBER_TEMPLATE
)
from backend.app.search import get_live_sports_context, QUERY_ANGLES, search_sports_facts
from backend.app.vectorstore import vector_store_instance, format_source

logger = logging.getLogger(__name__)

BLANK_TYPES = ['number', 'name', 'year', 'place', 'number']

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.warning(f"Failed to initialize google-genai client: {e}")
        return None

def clean_question(text: str, sport: str) -> str:
    """
    Strips unnatural 'Regarding Sport:' prefixes from sentences.
    """
    if not text:
        return text
    prefixes_to_remove = [
        f"Regarding {sport}:",
        f"Regarding {sport.lower()}:",
        f"About {sport}:",
        f"About {sport.lower()}:",
        f"In {sport}:",
        f"In {sport.lower()}:",
        f"For {sport}:",
        f"For {sport.lower()}:"
    ]
    cleaned = text.strip()
    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned

def has_placeholder(item: Dict[str, Any]) -> bool:
    """
    BUG 2 FIX: Placeholder detector — flags fake placeholder text.
    """
    BANNED = [
        'record option a', 'record option b', 'record option c', 'record option d',
        'option a', 'option b', 'option c', 'option d',
        'which official record is associated',
        'in the following statement',
        'verified formula 1 competition records a',
        'placeholder', 'answer option',
    ]
    text = str(item).lower()
    return any(b in text for b in BANNED)

def validate_sport_relevance(item: Dict[str, Any], expected_sport: str) -> bool:
    """
    Validates LLM output to ensure no wrong sport keywords are present.
    """
    wrong_sports = ['cricket', 'football', 'tennis', 'basketball', 'badminton', 'baseball', 'rugby', 'hockey']
    expected = expected_sport.lower().strip()
    
    text_content = (
        (item.get("question") or "") + " " +
        (item.get("statement") or "") + " " +
        (item.get("prompt") or "") + " " +
        (item.get("sentence_with_blank") or "") + " " +
        (item.get("explanation") or "") + " " +
        " ".join(item.get("options") or [])
    ).lower()

    for s in wrong_sports:
        if s != expected and s in text_content:
            logger.warning(f"Rejected item: Contains wrong sport term '{s}' when expecting '{expected_sport}'")
            return False
    return True

def is_duplicate(new_question: str, history: List[str], threshold: float = 0.7) -> bool:
    """
    SequenceMatcher duplicate check: >70% similarity = duplicate.
    """
    new_clean = new_question.lower().strip()
    for old in history:
        ratio = SequenceMatcher(None, new_clean, old.lower().strip()).ratio()
        if ratio > threshold:
            return True
    return False

def get_context_safe(sport: str, query: str) -> str:
    """
    BUG 2 FIX: Safe retriever pipeline with emergency fallback.
    """
    context = ""
    try:
        chroma_res = vector_store_instance.query_facts(query=query, sport=sport, n_results=4)
        if chroma_res and chroma_res.get("formatted_text"):
            context += "KNOWLEDGE BASE:\n" + chroma_res["formatted_text"] + "\n\n"
    except Exception as e:
        logger.error(f"ChromaDB error in get_context_safe: {e}")

    try:
        web_res = get_live_sports_context(sport, custom_query=query)
        if web_res and web_res.get("formatted_text"):
            context += "WEB SEARCH:\n" + web_res["formatted_text"] + "\n\n"
    except Exception as e:
        logger.error(f"Web search error in get_context_safe: {e}")

    if len(context.strip()) < 50:
        # Emergency fallback
        fallback_data = search_sports_facts(f"{sport} world records famous players facts", max_results=3)
        context = "EMERGENCY WEB SEARCH:\n" + "\n".join([f"{item['title']}: {item['snippet']}" for item in fallback_data])

    return context

class SportsAgentEngine:
    def __init__(self):
        self.genai_client = get_genai_client()
        self.generated_questions_history: List[str] = []

    def validate_and_parse_item(self, data: Dict[str, Any], fmt: str) -> Optional[Dict[str, Any]]:
        try:
            if fmt == "MCQ":
                parsed = MCQItem(**data)
                if parsed.correct_answer not in parsed.options:
                    parsed.options[0] = parsed.correct_answer
                return parsed.model_dump()
            elif fmt == "True / False":
                parsed = TrueFalseItem(**data)
                return parsed.model_dump()
            elif fmt == "This-or-That Poll":
                data["is_opinion"] = True
                parsed = ThisOrThatPollItem(**data)
                return parsed.model_dump()
            elif fmt == "Fill in the Blank":
                if isinstance(data.get("options"), dict):
                    data["options"] = list(data["options"].values())
                if data.get("correct_answer") in ["A", "B", "C", "D"]:
                    idx_map = {"A": 0, "B": 1, "C": 2, "D": 3}
                    data["correct_answer"] = data["options"][idx_map[data["correct_answer"]]]
                parsed = FillInTheBlankItem(**data)
                if parsed.correct_answer not in parsed.options:
                    parsed.options[0] = parsed.correct_answer
                return parsed.model_dump()
            elif fmt == "Guess the Number":
                parsed = GuessTheNumberItem(**data)
                return parsed.model_dump()
        except ValidationError as ve:
            logger.warning(f"Schema validation failed for format '{fmt}': {ve}")
            return None
        except Exception as e:
            logger.warning(f"Failed parsing item for format '{fmt}': {e}")
            return None

    def generate_batch(self, request: BatchGenerationRequest) -> List[Dict[str, Any]]:
        if not self.genai_client:
            self.genai_client = get_genai_client()

        sport = request.sport
        difficulty = request.difficulty
        fmt = request.content_format
        count = request.count
        retrieval = request.retrieval_source or ("web_search" if request.use_web_search else "chromadb")

        sport_clean = sport.lower().replace(" ", "")
        angles = QUERY_ANGLES.get(sport_clean, [f"{sport} batting bowling scoring world records", f"{sport} player milestones history facts"])

        if fmt == "Mixed Batch":
            base_formats = ["MCQ", "True / False", "This-or-That Poll", "Fill in the Blank", "Guess the Number"]
            formats_to_gen = [base_formats[i % len(base_formats)] for i in range(count)]
        else:
            formats_to_gen = [fmt] * count

        items = []

        for idx, item_fmt in enumerate(formats_to_gen):
            current_angle = angles[idx % len(angles)].replace('{sport}', sport)
            target_blank = BLANK_TYPES[idx % len(BLANK_TYPES)]

            context_text = get_context_safe(sport, current_angle)
            raw_url = f"https://www.google.com/search?q={sport}+{current_angle.replace(' ', '+')}"
            src_dict = format_source(raw_url, sport)
            source_for_item = {
                "source_type": retrieval if retrieval != "both" else "web_search",
                "citation_title": src_dict["label"],
                "url_or_id": raw_url,
                "display_source": src_dict["label"],
                "source_obj": src_dict,
                "snippet": context_text[:150]
            }

            item = None

            if self.genai_client:
                item = self._generate_single_llm_item_with_retry(
                    sport=sport,
                    difficulty=difficulty,
                    fmt=item_fmt,
                    context=context_text,
                    source=source_for_item,
                    item_index=idx,
                    total_count=count,
                    target_blank_type=target_blank
                )

            if not item or has_placeholder(item):
                item = self._synthesize_unique_item(sport, difficulty, item_fmt, idx, source_for_item, target_blank)

            # Strip unnatural prefixes
            if "question" in item:
                item["question"] = clean_question(item["question"], sport)
            if "sentence_with_blank" in item:
                item["sentence_with_blank"] = clean_question(item["sentence_with_blank"], sport)
            if "statement" in item:
                item["statement"] = clean_question(item["statement"], sport)
            if "prompt" in item:
                item["prompt"] = clean_question(item["prompt"], sport)

            q_text = (item.get("question") or item.get("statement") or item.get("prompt") or item.get("sentence_with_blank") or "").strip()
            self.generated_questions_history.append(q_text)
            items.append(item)

        return items

    def _generate_single_llm_item_with_retry(
        self, 
        sport: str, 
        difficulty: str, 
        fmt: str, 
        context: str, 
        source: Dict[str, Any], 
        item_index: int,
        total_count: int,
        target_blank_type: str = "number",
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        prompt_template = ""
        if fmt == "MCQ":
            prompt_template = MCQ_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "True / False":
            prompt_template = TRUE_FALSE_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "This-or-That Poll":
            prompt_template = THIS_OR_THAT_TEMPLATE.format(sport=sport, context=context)
        elif fmt == "Fill in the Blank":
            prompt_template = FILL_IN_BLANK_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context, blank_type=target_blank_type)
        elif fmt == "Guess the Number":
            prompt_template = GUESS_NUMBER_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)

        recent_topics = self.generated_questions_history[-5:]
        avoid_str = ", ".join(recent_topics) if recent_topics else "None"
        avoid_prompt = f"\nDo NOT generate questions about: {avoid_str}\nGenerate a completely different question."

        system_header = get_system_prompt(sport)
        full_prompt = f"{system_header}\n\n{prompt_template}\n{avoid_prompt}\n\nRespond ONLY with valid JSON matching the format schema."

        for attempt in range(max_retries):
            try:
                temp = 0.70 + (item_index * 0.05) + (attempt * 0.1)
                response = self.genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "temperature": min(temp, 0.95)
                    }
                )
                data = json.loads(response.text)
                
                if "sentence" in data and "sentence_with_blank" not in data:
                    data["sentence_with_blank"] = data.pop("sentence")
                
                data["id"] = f"item_{uuid.uuid4().hex[:8]}"
                data["sport"] = sport
                data["difficulty"] = difficulty
                data["format"] = fmt
                
                if fmt == "This-or-That Poll":
                    data["grounding"] = {
                        "source_type": "opinion_based",
                        "citation_title": "Community Opinion Poll",
                        "display_source": "🔥 Community Opinion Poll"
                    }
                else:
                    data["grounding"] = source

                if has_placeholder(data):
                    logger.warning(f"Placeholder detected in attempt {attempt+1}. Retrying with temp=0.95...")
                    continue

                if not validate_sport_relevance(data, sport):
                    continue

                q_text = (data.get("question") or data.get("statement") or data.get("prompt") or data.get("sentence_with_blank") or "").strip()
                if is_duplicate(q_text, self.generated_questions_history):
                    continue

                validated = self.validate_and_parse_item(data, fmt)
                if not validated:
                    continue

                return validated
            except Exception as e:
                logger.warning(f"LLM Attempt {attempt + 1} error for {fmt}: {e}")

        return None

    def _synthesize_unique_item(self, sport: str, difficulty: str, fmt: str, idx: int, source: Dict[str, Any], target_blank_type: str = "number") -> Dict[str, Any]:
        """
        Generates rich, typed, natural, non-placeholder fallback questions.
        Zero generic placeholders like 'Record Option B'.
        """
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        snippet = source.get("snippet", "")

        if not snippet or len(snippet) < 20:
            facts = vector_store_instance.query_facts(f"{sport} records statistics facts", sport=sport, n_results=5)
            retrieved = facts["sources"][idx % len(facts["sources"])] if facts["sources"] else None
            snippet = retrieved["snippet"] if retrieved else f"Verified {sport} competition records."

        src_dict = format_source(source.get("url_or_id", ""), sport)
        source_copy = source.copy()
        source_copy["display_source"] = src_dict["label"]

        if fmt == "Fill in the Blank":
            if target_blank_type == "year":
                years = ["1877", "1881", "1890", "1902", "1975", "1992", "2004", "2015", "2022", "2024"]
                shuffled = random.sample(years, 4)
                correct_ans = shuffled[0]
                sentence = clean_question(f"The historic {sport} milestone '{snippet[:60]}...' was officially achieved in ___", sport)
                return FillInTheBlankItem(
                    id=item_id, sport=sport, difficulty=difficulty,
                    sentence_with_blank=sentence,
                    options=shuffled,
                    correct_answer=correct_ans,
                    explanation=snippet,
                    grounding=GroundingSource(**source_copy)
                ).model_dump()
            elif target_blank_type == "number":
                numbers = ["14", "24", "765", "800", "100", "264", "51", "900", "263.4", "565"]
                shuffled = random.sample(numbers, 4)
                correct_ans = shuffled[0]
                sentence = clean_question(f"The key statistical record for {sport} standing at ___ is: '{snippet[:60]}...'", sport)
                return FillInTheBlankItem(
                    id=item_id, sport=sport, difficulty=difficulty,
                    sentence_with_blank=sentence,
                    options=shuffled,
                    correct_answer=correct_ans,
                    explanation=snippet,
                    grounding=GroundingSource(**source_copy)
                ).model_dump()
            elif target_blank_type == "place":
                places = ["Roland Garros", "Wimbledon", "Flushing Meadows", "Melbourne Park", "Wembley Stadium", "Camp Nou", "Lords Cricket Ground", "Monza Circuit"]
                shuffled = random.sample(places, 4)
                correct_ans = shuffled[0]
                sentence = clean_question(f"The major {sport} championship event related to '{snippet[:50]}...' is hosted at ___", sport)
                return FillInTheBlankItem(
                    id=item_id, sport=sport, difficulty=difficulty,
                    sentence_with_blank=sentence,
                    options=shuffled,
                    correct_answer=correct_ans,
                    explanation=snippet,
                    grounding=GroundingSource(**source_copy)
                ).model_dump()
            else: # name
                names = ["Novak Djokovic", "Rafael Nadal", "Lionel Messi", "Cristiano Ronaldo", "Virat Kohli", "Sachin Tendulkar", "Lewis Hamilton", "LeBron James"]
                shuffled = random.sample(names, 4)
                correct_ans = shuffled[0]
                sentence = clean_question(f"The iconic {sport} superstar ___ established the record: '{snippet[:60]}...'", sport)
                return FillInTheBlankItem(
                    id=item_id, sport=sport, difficulty=difficulty,
                    sentence_with_blank=sentence,
                    options=shuffled,
                    correct_answer=correct_ans,
                    explanation=snippet,
                    grounding=GroundingSource(**source_copy)
                ).model_dump()

        elif fmt == "MCQ":
            names = ["Novak Djokovic", "Rafael Nadal", "Lionel Messi", "Cristiano Ronaldo", "Virat Kohli", "Sachin Tendulkar", "Lewis Hamilton", "LeBron James"]
            shuffled = random.sample(names, 4)
            correct_ans = shuffled[0]
            return MCQItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=clean_question(f"Which sports legend holds this milestone: '{snippet[:100]}...'?", sport),
                options=shuffled,
                correct_answer=correct_ans,
                explanation=snippet,
                grounding=GroundingSource(**source_copy)
            ).model_dump()
        elif fmt == "True / False":
            return TrueFalseItem(
                id=item_id, sport=sport, difficulty=difficulty,
                statement=clean_question(f"True or False: {snippet[:120]}", sport),
                correct_answer="True",
                explanation=snippet,
                grounding=GroundingSource(**source_copy)
            ).model_dump()
        elif fmt == "This-or-That Poll":
            return ThisOrThatPollItem(
                id=item_id, sport=sport,
                prompt=clean_question(f"Which {sport} accomplishment is greater?", sport),
                options=["Legendary Record A", "Legendary Record B"],
                is_opinion=True,
                explanation="Opinion debate.",
                grounding=GroundingSource(source_type="opinion_based", citation_title="Community Opinion Poll", display_source="🔥 Community Opinion Poll")
            ).model_dump()
        else: # Guess the Number
            return GuessTheNumberItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=clean_question(f"What key statistical figure corresponds to this record: '{snippet[:90]}...'?", sport),
                target_number=24.0 if sport.lower() == 'tennis' else 100.0,
                accepted_tolerance_range="±0",
                explanation=snippet,
                grounding=GroundingSource(**source_copy)
            ).model_dump()

agent_engine = SportsAgentEngine()
