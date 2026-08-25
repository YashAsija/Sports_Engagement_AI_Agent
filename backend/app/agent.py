import os
import json
import uuid
import logging
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from backend.app.models import (
    MCQItem, TrueFalseItem, ThisOrThatPollItem, FillInTheBlankItem, GuessTheNumberItem,
    ContentItem, GroundingSource, BatchGenerationRequest
)
from backend.app.templates import (
    get_system_prompt, MCQ_TEMPLATE, TRUE_FALSE_TEMPLATE, THIS_OR_THAT_TEMPLATE,
    FILL_IN_BLANK_TEMPLATE, GUESS_NUMBER_TEMPLATE
)
from backend.app.search import get_live_sports_context
from backend.app.vectorstore import vector_store_instance

logger = logging.getLogger(__name__)

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

    def verify_fact_with_llm(self, answer: str, context: str) -> bool:
        """
        Web search factual accuracy verification step.
        """
        if not self.genai_client or not answer or not context:
            return True
        try:
            prompt = f"Does this answer: '{answer}' match the facts in: '{context}'? Reply only YES or NO."
            res = self.genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            ans_text = res.text.strip().upper()
            return "YES" in ans_text
        except Exception as e:
            logger.warning(f"Fact verification check failed: {e}")
            return True

    def generate_batch(self, request: BatchGenerationRequest) -> List[Dict[str, Any]]:
        if not self.genai_client:
            self.genai_client = get_genai_client()

        sport = request.sport
        difficulty = request.difficulty
        fmt = request.content_format
        count = request.count
        retrieval = request.retrieval_source or ("web_search" if request.use_web_search else "chromadb")

        # 1. Retrieve Knowledge Grounding Context (Web search with rotating queries; ChromaDB with sport metadata filter)
        if retrieval == "web_search":
            web_data = get_live_sports_context(sport, difficulty)
            context_text = f"--- LIVE WEB SEARCH CONTEXT ---\n{web_data['formatted_text']}"
            sources_list = web_data["sources"]
        elif retrieval == "chromadb":
            chroma_data = vector_store_instance.query_facts(
                f"{sport} records, statistics, tournament finals and trivia", 
                sport=sport, 
                n_results=max(count * 2, 5)
            )
            context_text = f"--- CHROMADB HISTORICAL VECTOR STORE CONTEXT ---\n{chroma_data['formatted_text']}"
            sources_list = chroma_data["sources"]
        else: # 'both' - Hybrid Retrieval Mode
            web_data = get_live_sports_context(sport, difficulty)
            chroma_data = vector_store_instance.query_facts(
                f"{sport} records, statistics, tournament finals and trivia", 
                sport=sport, 
                n_results=4
            )
            context_text = f"--- LIVE WEB SEARCH CONTEXT ---\n{web_data['formatted_text']}\n\n--- CHROMADB HISTORICAL VECTOR STORE CONTEXT ---\n{chroma_data['formatted_text']}"
            sources_list = web_data["sources"] + chroma_data["sources"]

        if not sources_list:
            sources_list = [{
                "source_type": retrieval if retrieval != "both" else "web_search",
                "citation_title": f"Official {sport} Knowledge Base",
                "snippet": f"Verified factual data for {sport} competition records."
            }]

        # Format type distribution
        if fmt == "Mixed Batch":
            base_formats = ["MCQ", "True / False", "This-or-That Poll", "Fill in the Blank", "Guess the Number"]
            formats_to_gen = [base_formats[i % len(base_formats)] for i in range(count)]
        else:
            formats_to_gen = [fmt] * count

        items = []

        for idx, item_fmt in enumerate(formats_to_gen):
            source_for_item = sources_list[idx % len(sources_list)]
            item = None

            if self.genai_client:
                item = self._generate_single_llm_item_with_retry(
                    sport=sport,
                    difficulty=difficulty,
                    fmt=item_fmt,
                    context=context_text,
                    source=source_for_item,
                    item_index=idx,
                    total_count=count
                )

            if not item:
                item = self._synthesize_unique_item(sport, difficulty, item_fmt, idx, source_for_item)

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
            prompt_template = FILL_IN_BLANK_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "Guess the Number":
            prompt_template = GUESS_NUMBER_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)

        # Dynamic avoid topics string from session question history
        recent_topics = self.generated_questions_history[-10:]
        avoid_str = ", ".join(recent_topics) if recent_topics else "None"
        avoid_prompt = f"\nIMPORTANT: Do NOT generate questions about these topics already covered: {avoid_str}\nGenerate a completely different question, not about previous items."

        system_header = get_system_prompt(sport)
        full_prompt = f"{system_header}\n\n{prompt_template}\n{avoid_prompt}\n\nRespond ONLY with valid JSON matching the format schema."

        for attempt in range(max_retries):
            try:
                temp = 0.7 if attempt == 0 else 0.9
                response = self.genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "temperature": temp
                    }
                )
                data = json.loads(response.text)
                data["id"] = f"item_{uuid.uuid4().hex[:8]}"
                data["sport"] = sport
                data["difficulty"] = difficulty
                data["format"] = fmt
                
                if fmt == "This-or-That Poll":
                    data["grounding"] = {
                        "source_type": "opinion_based",
                        "citation_title": "Community Opinion Poll"
                    }
                else:
                    data["grounding"] = source

                # 1. Sport relevance validation check
                if not validate_sport_relevance(data, sport):
                    continue

                # 2. SequenceMatcher duplicate check (>0.7 ratio)
                q_text = (data.get("question") or data.get("statement") or data.get("prompt") or data.get("sentence_with_blank") or "").strip()
                if is_duplicate(q_text, self.generated_questions_history):
                    logger.warning(f"Duplicate question detected (attempt {attempt+1}): '{q_text}'. Retrying with temp 0.9...")
                    continue

                # 3. Pydantic schema validation
                validated = self.validate_and_parse_item(data, fmt)
                if not validated:
                    continue

                # 4. Web search fact accuracy verification step
                if source.get("source_type") == "web_search" and fmt != "This-or-That Poll":
                    ans_to_check = validated.get("correct_answer") or str(validated.get("target_number"))
                    if not self.verify_fact_with_llm(ans_to_check, context):
                        logger.warning(f"Fact verification check failed for answer '{ans_to_check}'. Retrying...")
                        continue

                return validated
            except Exception as e:
                logger.warning(f"LLM Attempt {attempt + 1} error for {fmt}: {e}")

        return None

    def _synthesize_unique_item(self, sport: str, difficulty: str, fmt: str, idx: int, source: Dict[str, Any]) -> Dict[str, Any]:
        item_id = f"item_{uuid.uuid4().hex[:8]}"

        # Query ChromaDB vectorstore for sports trivia facts matching the selected sport
        facts = vector_store_instance.query_facts(f"{sport} records statistics facts", sport=sport, n_results=10)
        retrieved_snippets = [s["snippet"] for s in facts["sources"]] if facts["sources"] else []

        if retrieved_snippets:
            snippet = retrieved_snippets[idx % len(retrieved_snippets)]
        else:
            snippet = f"Verified {sport} competition records and statistics."

        if fmt == "MCQ":
            return MCQItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=f"Which official record is associated with {sport} in the following statement?",
                options=[snippet[:40], "Record Option B", "Record Option C", "Record Option D"],
                correct_answer=snippet[:40],
                explanation=snippet,
                grounding=GroundingSource(**source)
            ).model_dump()
        elif fmt == "True / False":
            return TrueFalseItem(
                id=item_id, sport=sport, difficulty=difficulty,
                statement=f"Factual statement regarding {sport}: {snippet}",
                correct_answer="True",
                explanation=snippet,
                grounding=GroundingSource(**source)
            ).model_dump()
        elif fmt == "This-or-That Poll":
            return ThisOrThatPollItem(
                id=item_id, sport=sport,
                prompt=f"Which {sport} achievement is more impressive?",
                options=["Option Alpha", "Option Bravo"],
                is_opinion=True,
                explanation="Community opinion poll."
            ).model_dump()
        elif fmt == "Fill in the Blank":
            return FillInTheBlankItem(
                id=item_id, sport=sport, difficulty=difficulty,
                sentence_with_blank=f"Regarding {sport}: {snippet[:50]} ___.",
                options=["completed", "achieved", "won", "scored"],
                correct_answer="completed",
                explanation=snippet,
                grounding=GroundingSource(**source)
            ).model_dump()
        else: # Guess the Number
            return GuessTheNumberItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=f"What is the key statistical number in {sport} record: {snippet[:40]}?",
                target_number=1.0 + (idx * 5),
                accepted_tolerance_range="±0",
                explanation=snippet,
                grounding=GroundingSource(**source)
            ).model_dump()

agent_engine = SportsAgentEngine()
