import os
import json
from enum import Enum
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

class SportType(str, Enum):
    CRICKET = "Cricket"
    FOOTBALL = "Football"
    TENNIS = "Tennis"
    BASKETBALL = "Basketball"
    BADMINTON = "Badminton"
    FORMULA_1 = "Formula 1"
    VOLLEYBALL = "Volleyball"

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class ContentFormat(str, Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "True / False"
    THIS_OR_THAT = "This-or-That Poll"
    FILL_IN_BLANK = "Fill in the Blank"
    GUESS_NUMBER = "Guess the Number"

class GroundingSource(BaseModel):
    source_type: Literal["web_search", "chromadb", "opinion_based", "fallback_verified"] = "web_search"
    citation_title: str = Field(description="Name or title of the retrieved source")
    url_or_id: Optional[str] = Field(default=None, description="URL or Document ID")
    snippet: Optional[str] = Field(default=None, description="Excerpt supporting the factual statement")

# 1. Multiple Choice Question (MCQ)
class MCQItem(BaseModel):
    id: str
    format: Literal["MCQ"] = "MCQ"
    sport: str
    difficulty: str
    question: str = Field(description="The quiz question text")
    options: List[str] = Field(description="Exactly 4 distinct answer options")
    correct_answer: str = Field(description="The exact text matching one of the options")
    explanation: str = Field(description="Short factual explanation grounding the answer")
    grounding: GroundingSource

# 2. True / False
class TrueFalseItem(BaseModel):
    id: str
    format: Literal["True / False"] = "True / False"
    sport: str
    difficulty: str
    statement: str = Field(description="Factual statement that is either True or False")
    correct_answer: Literal["True", "False"] = Field(description="Whether the statement is True or False")
    explanation: str = Field(description="Short factual explanation grounding the answer")
    grounding: GroundingSource

# 3. This-or-That Poll
class ThisOrThatPollItem(BaseModel):
    id: str
    format: Literal["This-or-That Poll"] = "This-or-That Poll"
    sport: str
    prompt: str = Field(description="Opinion question comparing two items/players/teams")
    options: List[str] = Field(description="Exactly 2 options for comparison")
    is_opinion: bool = Field(default=True, description="Flagged as opinion-based, not fact-checked")
    explanation: str = Field(default="Pure opinion poll for Instagram community engagement", description="Context about the debate")
    grounding: GroundingSource = Field(default_factory=lambda: GroundingSource(source_type="opinion_based", citation_title="Community Opinion Poll"))

# 4. Fill in the Blank
class FillInTheBlankItem(BaseModel):
    id: str
    format: Literal["Fill in the Blank"] = "Fill in the Blank"
    sport: str
    difficulty: str
    sentence_with_blank: str = Field(description="Sentence containing '___' indicating the missing word/phrase")
    options: List[str] = Field(description="Exactly 4 answer options to complete the blank")
    correct_answer: str = Field(description="The correct word/phrase matching one option")
    explanation: str = Field(description="Short factual explanation")
    grounding: GroundingSource

# 5. Guess the Number
class GuessTheNumberItem(BaseModel):
    id: str
    format: Literal["Guess the Number"] = "Guess the Number"
    sport: str
    difficulty: str
    question: str = Field(description="Numerical trivia question e.g. 'How many goals did Messi score in 2012?'")
    target_number: float = Field(description="The exact numeric answer")
    accepted_tolerance_range: str = Field(description="Formatted string e.g. '±5' or '90 - 92'")
    explanation: str = Field(description="Short factual context detailing the number")
    grounding: GroundingSource

ContentItem = Union[MCQItem, TrueFalseItem, ThisOrThatPollItem, FillInTheBlankItem, GuessTheNumberItem]

class BatchGenerationRequest(BaseModel):
    sport: str = "Cricket"
    difficulty: str = "Medium"
    content_format: str = "Mixed Batch"
    count: int = 5
    retrieval_source: str = "both" # "web_search", "chromadb", "both"
    use_web_search: Optional[bool] = True

class SingleItemRegenerateRequest(BaseModel):
    sport: str
    difficulty: str
    content_format: str
    target_item_id: str
    existing_batch_ids: List[str] = []
    retrieval_source: str = "both" # "web_search", "chromadb", "both"
    use_web_search: Optional[bool] = True

class BatchGenerationResponse(BaseModel):
    sport: str
    difficulty: str
    items: List[ContentItem]
    generated_at: str
