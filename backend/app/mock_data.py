"""
Realistic fallback items for offline/simulation mode ensuring 100% reliable demo.
"""

MOCK_BATCH_ITEMS = {
    "Cricket": [
        {
            "id": "item_cric_1",
            "format": "MCQ",
            "sport": "Cricket",
            "difficulty": "Medium",
            "question": "Who holds the record for the most runs in a single ICC ODI Cricket World Cup edition?",
            "options": ["Sachin Tendulkar", "Virat Kohli", "Rohit Sharma", "Ricky Ponting"],
            "correct_answer": "Virat Kohli",
            "explanation": "Virat Kohli scored 765 runs in 11 innings during the 2023 World Cup, surpassing Sachin Tendulkar's 2003 record of 673 runs.",
            "grounding": {
                "source_type": "chromadb",
                "citation_title": "Virat Kohli 2023 World Cup Record",
                "url_or_id": "chroma://cric_001",
                "snippet": "Virat Kohli scored 765 runs in the 2023 ICC Cricket World Cup, breaking Sachin Tendulkar's record."
            }
        },
        {
            "id": "item_cric_2",
            "format": "True / False",
            "sport": "Cricket",
            "difficulty": "Medium",
            "statement": "AB de Villiers scored the fastest century in ODI cricket history off just 31 balls.",
            "correct_answer": "True",
            "explanation": "AB de Villiers reached his century in 31 balls against the West Indies at Johannesburg on January 18, 2015.",
            "grounding": {
                "source_type": "chromadb",
                "citation_title": "Fastest ODI Century",
                "url_or_id": "chroma://cric_002",
                "snippet": "AB de Villiers holds the record for the fastest century in ODI cricket, scored in 31 balls."
            }
        },
        {
            "id": "item_cric_3",
            "format": "This-or-That Poll",
            "sport": "Cricket",
            "prompt": "Cover Drive King — Virat Kohli or Babar Azam?",
            "options": ["Virat Kohli", "Babar Azam"],
            "is_opinion": True,
            "explanation": "Pure opinion poll for Instagram community engagement on technical strokes.",
            "grounding": {
                "source_type": "opinion_based",
                "citation_title": "Community Opinion Poll"
            }
        },
        {
            "id": "item_cric_4",
            "format": "Fill in the Blank",
            "sport": "Cricket",
            "difficulty": "Medium",
            "sentence_with_blank": "The highest individual score in Test cricket history is 400 not out, scored by ___ against England in 2004.",
            "options": ["Brian Lara", "Virender Sehwag", "Matthew Hayden", "Kumar Sangakkara"],
            "correct_answer": "Brian Lara",
            "explanation": "Brian Lara scored 400* against England in St. John's, Antigua in April 2004.",
            "grounding": {
                "source_type": "web_search",
                "citation_title": "Test Cricket Highest Individual Scores",
                "url_or_id": "https://www.espncricinfo.com",
                "snippet": "Brian Lara's 400* remains the highest individual score in Test match history."
            }
        },
        {
            "id": "item_cric_5",
            "format": "Guess the Number",
            "sport": "Cricket",
            "difficulty": "Hard",
            "question": "How many career international centuries has Sachin Tendulkar scored across Tests and ODIs?",
            "target_number": 100,
            "accepted_tolerance_range": "±0",
            "explanation": "Sachin Tendulkar scored 51 Test centuries and 49 ODI centuries, making a historic 100 international centuries.",
            "grounding": {
                "source_type": "fallback_verified",
                "citation_title": "International Cricket Records",
                "snippet": "Sachin Tendulkar is the only cricketer to score 100 international centuries."
            }
        }
    ],
    "Football": [
        {
            "id": "item_foot_1",
            "format": "MCQ",
            "sport": "Football",
            "difficulty": "Easy",
            "question": "Which country won the FIFA Men's World Cup in Qatar 2022?",
            "options": ["France", "Argentina", "Brazil", "Croatia"],
            "correct_answer": "Argentina",
            "explanation": "Argentina defeated France 4-2 on penalties after a 3-3 draw in one of the greatest World Cup finals in history.",
            "grounding": {
                "source_type": "web_search",
                "citation_title": "FIFA World Cup 2022 Final Results",
                "url_or_id": "https://www.fifa.com",
                "snippet": "Argentina won the 2022 World Cup in Qatar led by Lionel Messi."
            }
        },
        {
            "id": "item_foot_2",
            "format": "True / False",
            "sport": "Football",
            "difficulty": "Medium",
            "statement": "Lionel Messi scored 91 official goals in a single calendar year in 2012.",
            "correct_answer": "True",
            "explanation": "Messi scored 91 goals in 2012 (79 for Barcelona and 12 for Argentina), breaking Gerd Müller's record.",
            "grounding": {
                "source_type": "chromadb",
                "citation_title": "Lionel Messi 91 Goals Record",
                "url_or_id": "chroma://foot_001",
                "snippet": "Lionel Messi scored a record 91 goals in a single calendar year (2012)."
            }
        },
        {
            "id": "item_foot_3",
            "format": "This-or-That Poll",
            "sport": "Football",
            "prompt": "Better Champions League comeback: Liverpool 4-0 Barca (2019) or Real Madrid vs Man City (2022)?",
            "options": ["Liverpool vs Barca", "Real Madrid vs Man City"],
            "is_opinion": True,
            "explanation": "Debate post comparing two iconic Champions League miracle turnarounds.",
            "grounding": {
                "source_type": "opinion_based",
                "citation_title": "Community Opinion Poll"
            }
        },
        {
            "id": "item_foot_4",
            "format": "Fill in the Blank",
            "sport": "Football",
            "difficulty": "Medium",
            "sentence_with_blank": "Real Madrid secured their ___ UEFA Champions League title in June 2024 by defeating Borussia Dortmund.",
            "options": ["13th", "14th", "15th", "16th"],
            "correct_answer": "15th",
            "explanation": "Real Madrid won their 15th European crown at Wembley Stadium in June 2024.",
            "grounding": {
                "source_type": "chromadb",
                "citation_title": "Real Madrid Champions League Titles",
                "url_or_id": "chroma://foot_002",
                "snippet": "Real Madrid won their 15th UEFA Champions League title in 2024."
            }
        },
        {
            "id": "item_foot_5",
            "format": "Guess the Number",
            "sport": "Football",
            "difficulty": "Medium",
            "question": "How many Ballon d'Or awards has Lionel Messi won in his career?",
            "target_number": 8,
            "accepted_tolerance_range": "±0",
            "explanation": "Lionel Messi won his record 8th Ballon d'Or trophy in October 2023.",
            "grounding": {
                "source_type": "web_search",
                "citation_title": "Ballon d'Or Historical Winners",
                "url_or_id": "https://www.francefootball.fr",
                "snippet": "Lionel Messi won his 8th Ballon d'Or award in 2023."
            }
        }
    ]
}
