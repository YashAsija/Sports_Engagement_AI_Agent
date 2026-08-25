import pytest
from backend.app.models import (
    MCQItem, TrueFalseItem, ThisOrThatPollItem, FillInTheBlankItem, GuessTheNumberItem, GroundingSource
)
from backend.app.agent import agent_engine, BatchGenerationRequest

def test_mcq_schema_validation():
    grounding = GroundingSource(source_type="chromadb", citation_title="Test", snippet="Test snippet")
    item = MCQItem(
        id="test_1",
        sport="Cricket",
        difficulty="Easy",
        question="What is the maximum number of overs per bowler in ODIs?",
        options=["5", "10", "12", "15"],
        correct_answer="10",
        explanation="Standard ODI rules limit each bowler to 10 overs in cricket.",
        grounding=grounding
    )
    assert len(item.options) == 4
    assert item.correct_answer in item.options

def test_poll_schema_validation():
    item = ThisOrThatPollItem(
        id="test_2",
        sport="Football",
        prompt="Prime Ronaldinho vs Prime Neymar — who was more entertaining?",
        options=["Ronaldinho", "Neymar"]
    )
    assert len(item.options) == 2
    assert item.is_opinion is True

def test_guess_number_schema_validation():
    grounding = GroundingSource(source_type="fallback_verified", citation_title="Test", snippet="Test snippet")
    item = GuessTheNumberItem(
        id="test_3",
        sport="Basketball",
        difficulty="Medium",
        question="How many total points did Wilt Chamberlain score in his iconic 1962 NBA basketball game?",
        target_number=100.0,
        accepted_tolerance_range="±0",
        explanation="Wilt Chamberlain scored 100 points in basketball.",
        grounding=grounding
    )
    assert item.target_number == 100.0

def test_batch_generation_simulation():
    req = BatchGenerationRequest(sport="Cricket", difficulty="Medium", content_format="Mixed Batch", count=5)
    items = agent_engine.generate_batch(req)
    assert len(items) == 5
    formats = [it["format"] for it in items]
    assert "MCQ" in formats
    assert "True / False" in formats

def test_agent_schema_validation_function():
    valid_mcq = {
        "id": "mcq_1",
        "sport": "Tennis",
        "difficulty": "Hard",
        "question": "How many Roland Garros singles titles has Rafael Nadal won in tennis?",
        "options": ["10", "12", "14", "16"],
        "correct_answer": "14",
        "explanation": "Rafael Nadal won 14 French Open tennis titles.",
        "grounding": {"source_type": "chromadb", "citation_title": "Nadal Record", "snippet": "14 titles."}
    }
    validated = agent_engine.validate_and_parse_item(valid_mcq, "MCQ")
    assert validated is not None
    assert len(validated["options"]) == 4

    invalid_mcq = {
        "id": "mcq_wrong_sport",
        "sport": "Cricket",
        "difficulty": "Easy",
        "question": "Which football team won the Champions League?", # Mentioning football when sport=cricket
        "options": ["Real Madrid", "Barcelona", "Bayern", "PSG"],
        "correct_answer": "Real Madrid",
        "explanation": "Real Madrid won the football trophy.",
        "grounding": {"source_type": "web_search", "citation_title": "Wrong Sport", "snippet": "Football match."}
    }
    invalid_validated = agent_engine.validate_and_parse_item(invalid_mcq, "MCQ")
    assert invalid_validated is None
