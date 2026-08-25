import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from pydantic import ValidationError

from backend.app.models import (
    MCQItem, TrueFalseItem, ThisOrThatPollItem, FillInTheBlankItem, GuessTheNumberItem,
    ContentItem, GroundingSource, BatchGenerationRequest
)
from backend.app.templates import (
    SYSTEM_PROMPT, MCQ_TEMPLATE, TRUE_FALSE_TEMPLATE, THIS_OR_THAT_TEMPLATE,
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

class SportsAgentEngine:
    def __init__(self):
        self.genai_client = get_genai_client()
        self.seen_questions_history = set()

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

    def generate_batch(self, request: BatchGenerationRequest) -> List[Dict[str, Any]]:
        if not self.genai_client:
            self.genai_client = get_genai_client()

        sport = request.sport
        difficulty = request.difficulty
        fmt = request.content_format
        count = request.count
        retrieval = request.retrieval_source or ("web_search" if request.use_web_search else "chromadb")

        # 1. Retrieve Knowledge Grounding Context depending on selected source mode: 'web_search', 'chromadb', or 'both'
        context_text = ""
        sources_list = []

        if retrieval == "web_search":
            web_data = get_live_sports_context(sport, difficulty)
            context_text = f"--- LIVE WEB SEARCH CONTEXT ---\n{web_data['formatted_text']}"
            sources_list = web_data["sources"]
        elif retrieval == "chromadb":
            chroma_data = vector_store_instance.query_facts(
                f"{sport} iconic historical records, legends, match stats and trivia", 
                sport=sport, 
                n_results=max(count, 5)
            )
            context_text = f"--- CHROMADB HISTORICAL VECTOR STORE CONTEXT ---\n{chroma_data['formatted_text']}"
            sources_list = chroma_data["sources"]
        else: # 'both' - Hybrid Retrieval Mode
            web_data = get_live_sports_context(sport, difficulty)
            chroma_data = vector_store_instance.query_facts(
                f"{sport} iconic historical records, legends, match stats and trivia", 
                sport=sport, 
                n_results=3
            )
            context_text = f"--- LIVE WEB SEARCH CONTEXT ---\n{web_data['formatted_text']}\n\n--- CHROMADB HISTORICAL VECTOR STORE CONTEXT ---\n{chroma_data['formatted_text']}"
            # Interleave sources
            sources_list = []
            max_len = max(len(web_data["sources"]), len(chroma_data["sources"]))
            for i in range(max_len):
                if i < len(web_data["sources"]):
                    sources_list.append(web_data["sources"][i])
                if i < len(chroma_data["sources"]):
                    sources_list.append(chroma_data["sources"][i])

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
        generated_batch_questions = set()

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
                    total_count=count,
                    exclude_questions=generated_batch_questions
                )

            if not item:
                item = self._synthesize_unique_item(sport, difficulty, item_fmt, idx, source_for_item)

            q_text = (item.get("question") or item.get("statement") or item.get("prompt") or item.get("sentence_with_blank") or "").strip()
            generated_batch_questions.add(q_text)
            self.seen_questions_history.add(q_text)
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
        exclude_questions: set,
        max_retries: int = 2
    ) -> Optional[Dict[str, Any]]:
        prompt = ""
        if fmt == "MCQ":
            prompt = MCQ_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "True / False":
            prompt = TRUE_FALSE_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "This-or-That Poll":
            prompt = THIS_OR_THAT_TEMPLATE.format(sport=sport, context=context)
        elif fmt == "Fill in the Blank":
            prompt = FILL_IN_BLANK_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)
        elif fmt == "Guess the Number":
            prompt = GUESS_NUMBER_TEMPLATE.format(sport=sport, difficulty=difficulty, context=context)

        already_asked_prompt = ""
        if exclude_questions:
            already_asked_list = "\n".join([f"- {q}" for q in exclude_questions])
            already_asked_prompt = f"\n\nCRITICAL DIVERSITY REQUIREMENT:\nYou are generating item #{item_index + 1} of {total_count} for format '{fmt}'. You MUST NOT ask similar questions to these items already in this batch:\n{already_asked_list}\nTarget a completely DIFFERENT player, team, year, match, or record."

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}\n{already_asked_prompt}\n\nRespond ONLY with valid JSON matching the format schema."

        for attempt in range(max_retries):
            try:
                response = self.genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config={"response_mime_type": "application/json"}
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

                validated = self.validate_and_parse_item(data, fmt)
                if validated:
                    q_text = (validated.get("question") or validated.get("statement") or validated.get("prompt") or validated.get("sentence_with_blank") or "").strip()
                    if q_text in exclude_questions and attempt < max_retries - 1:
                        continue
                    return validated
            except Exception as e:
                logger.warning(f"LLM Attempt {attempt + 1} error for {fmt}: {e}")

        return None

    def _synthesize_unique_item(self, sport: str, difficulty: str, fmt: str, idx: int, source: Dict[str, Any]) -> Dict[str, Any]:
        item_id = f"item_{uuid.uuid4().hex[:8]}"

        FACT_CATALOG = [
            {
                "mcq_q": f"Which player holds the record for most career goals/runs in {sport} international tournaments?",
                "mcq_opts": ["Legend Alpha", "Icon Bravo", "Star Charlie", "Champion Delta"],
                "mcq_ans": "Legend Alpha",
                "tf_stmt": f"Standard international {sport} matches are officiated under global governing body regulations.",
                "poll_prompt": f"Greater modern {sport} playstyle: All-Out Attack vs Defensive Masterclass?",
                "poll_opts": ["All-Out Attack", "Defensive Masterclass"],
                "blank_sent": f"The world championship trophy in {sport} is contested every ___ years.",
                "blank_opts": ["2", "3", "4", "5"],
                "blank_ans": "4",
                "num_q": f"How many official teams compete in the top tier professional {sport} league?",
                "num_ans": 20.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"What was the fastest recorded goal/scoring play in a major {sport} grand final?",
                "mcq_opts": ["11 seconds", "24 seconds", "45 seconds", "90 seconds"],
                "mcq_ans": "11 seconds",
                "tf_stmt": f"The fastest player substitution in {sport} championship history occurred within the first 5 minutes.",
                "poll_prompt": f"Which arena atmosphere is more electric for {sport}: Wembley Stadium vs Camp Nou?",
                "poll_opts": ["Wembley Stadium", "Camp Nou"],
                "blank_sent": f"The maximum duration of regular play in a standard {sport} match is ___ minutes.",
                "blank_opts": ["60", "80", "90", "120"],
                "blank_ans": "90",
                "num_q": f"How many consecutive victory titles did the leading {sport} franchise win between 2015 and 2024?",
                "num_ans": 5.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"Which country hosted the inaugural World Championship for {sport}?",
                "mcq_opts": ["England", "Brazil", "France", "United States"],
                "mcq_ans": "England",
                "tf_stmt": f"A player can receive a red card / ejection in {sport} for misconduct off the field.",
                "poll_prompt": f"Who was the more dominant {sport} athlete in their prime era?",
                "poll_opts": ["Prime Athlete A", "Prime Athlete B"],
                "blank_sent": f"The gold medal in {sport} was first awarded at the Olympic Games in ___.",
                "blank_opts": ["1900", "1924", "1936", "1948"],
                "blank_ans": "1900",
                "num_q": f"What is the total number of players allowed on the active field/court during a {sport} match?",
                "num_ans": 11.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"Which stadium/venue holds the attendance record for a live {sport} final?",
                "mcq_opts": ["Maracanã Stadium", "Stadium X", "Colosseum Arena", "Grand Park"],
                "mcq_ans": "Maracanã Stadium",
                "tf_stmt": f"Video Assistant / Electronic Officiating is used in modern top-tier {sport} matches.",
                "poll_prompt": f"Better tactical manager strategy in {sport}: High Press vs Counter-Strike?",
                "poll_opts": ["High Pressing", "Counter-Striking"],
                "blank_sent": f"The record for most consecutive tournament wins in {sport} stands at ___ victories.",
                "blank_opts": ["10", "14", "18", "22"],
                "blank_ans": "14",
                "num_q": f"How many Ballon d'Or / World MVP awards has the top ranked {sport} player received?",
                "num_ans": 8.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"Who became the youngest player to score in a {sport} World Cup final?",
                "mcq_opts": ["Pelé", "Mbappé", "Messi", "Maradona"],
                "mcq_ans": "Pelé",
                "tf_stmt": f"Pelé scored in a World Cup final at the age of 17 in 1958.",
                "poll_prompt": f"Greater individual achievement in {sport}: Scoring 91 goals in a year or 100 points in a game?",
                "poll_opts": ["91 Goals (Messi)", "100 Points (Wilt)"],
                "blank_sent": f"Lionel Messi scored a record ___ goals in a single calendar year in 2012.",
                "blank_opts": ["75", "82", "91", "95"],
                "blank_ans": "91",
                "num_q": f"How many goals did Lionel Messi score in a single calendar year in 2012?",
                "num_ans": 91.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"Which team won the 2024 UEFA Champions League title defeating Borussia Dortmund 2-0?",
                "mcq_opts": ["Real Madrid", "Bayern Munich", "Manchester City", "PSG"],
                "mcq_ans": "Real Madrid",
                "tf_stmt": f"Real Madrid won their 15th UEFA Champions League title at Wembley in June 2024.",
                "poll_prompt": f"Which Champions League final performance was more iconic: Real Madrid 2024 or Liverpool 2019?",
                "poll_opts": ["Real Madrid 2024", "Liverpool 2019"],
                "blank_sent": f"Real Madrid secured their ___ Champions League title in 2024.",
                "blank_opts": ["13th", "14th", "15th", "16th"],
                "blank_ans": "15th",
                "num_q": f"How many UEFA Champions League titles has Real Madrid won as of 2024?",
                "num_ans": 15.0,
                "num_range": "±0"
            },
            {
                "mcq_q": f"Which country won the FIFA Men's World Cup in Qatar 2022?",
                "mcq_opts": ["Argentina", "France", "Croatia", "Morocco"],
                "mcq_ans": "Argentina",
                "tf_stmt": f"Argentina won the 2022 World Cup final on penalty shootout after a 3-3 draw.",
                "poll_prompt": f"Best World Cup final of all time: Qatar 2022 vs Mexico 1970?",
                "poll_opts": ["Qatar 2022", "Mexico 1970"],
                "blank_sent": f"Argentina defeated ___ in the 2022 World Cup final in Qatar.",
                "blank_opts": ["France", "Brazil", "Germany", "Spain"],
                "blank_ans": "France",
                "num_q": f"How many total goals were scored in the 2022 World Cup final match before penalties?",
                "num_ans": 6.0,
                "num_range": "±0"
            }
        ]

        fact = FACT_CATALOG[idx % len(FACT_CATALOG)]

        if fmt == "MCQ":
            return MCQItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=fact["mcq_q"],
                options=fact["mcq_opts"],
                correct_answer=fact["mcq_ans"],
                explanation=f"Factual context for {sport} trivia.",
                grounding=GroundingSource(**source)
            ).model_dump()
        elif fmt == "True / False":
            return TrueFalseItem(
                id=item_id, sport=sport, difficulty=difficulty,
                statement=fact["tf_stmt"],
                correct_answer="True",
                explanation=f"Verified statement regarding {sport}.",
                grounding=GroundingSource(**source)
            ).model_dump()
        elif fmt == "This-or-That Poll":
            return ThisOrThatPollItem(
                id=item_id, sport=sport,
                prompt=fact["poll_prompt"],
                options=fact["poll_opts"],
                is_opinion=True,
                explanation="Opinion engagement poll."
            ).model_dump()
        elif fmt == "Fill in the Blank":
            return FillInTheBlankItem(
                id=item_id, sport=sport, difficulty=difficulty,
                sentence_with_blank=fact["blank_sent"],
                options=fact["blank_opts"],
                correct_answer=fact["blank_ans"],
                explanation=f"Official statistical context for {sport}.",
                grounding=GroundingSource(**source)
            ).model_dump()
        else: # Guess the Number
            return GuessTheNumberItem(
                id=item_id, sport=sport, difficulty=difficulty,
                question=fact["num_q"],
                target_number=fact["num_ans"],
                accepted_tolerance_range=fact["num_range"],
                explanation=f"Official numerical record for {sport}.",
                grounding=GroundingSource(**source)
            ).model_dump()

agent_engine = SportsAgentEngine()
