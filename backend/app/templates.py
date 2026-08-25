"""
Type-specific prompt templates for generating sports engagement content formats.
"""

def get_system_prompt(sport: str) -> str:
    return f"""You are a {sport} quiz expert. You ONLY generate content about {sport}. Never mention any other sport. If retrieved context contains other sports, ignore it completely.

STRICT RULES:
1. All factual claims MUST be grounded in the provided Context.
2. DO NOT make up statistics or record numbers.
3. Keep questions concise and optimized for quick mobile reading.
4. NEVER start the sentence with 'Regarding {sport}:' or 'About {sport}:'. Write naturally as it would appear in a quiz.
5. Provide structured output in JSON format adhering strictly to the requested schema.
"""

MCQ_TEMPLATE = """
Generate a Multiple Choice Question (MCQ) for Instagram Story Quiz Sticker.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

QUALITY RULES — the question MUST be specific:
GOOD: 'How many F1 championships did Lewis Hamilton win?'
GOOD: 'Which year did India win the T20 World Cup under Rohit Sharma?'
BAD: 'Which official record is associated with this sport?'
BAD: 'Which of the following is correct?'

ALL 4 options must be real specific values. 
NEVER write 'Record Option B' or 'Option C' or any placeholder.
Do NOT start with 'Regarding {sport}:'.

Requirements:
- Question: Concise, engaging trivia question strictly about {sport}.
- Options: EXACTLY 4 distinct options (A, B, C, D).
- Correct Answer: Must match one of the 4 options exactly.
- Explanation: 1-2 sentence grounding explanation.
"""

TRUE_FALSE_TEMPLATE = """
Generate a True / False challenge for Instagram Story.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Statement: Clear factual statement strictly about {sport} that can be evaluated as strictly True or False. Do NOT start with 'Regarding {sport}:'.
- Correct Answer: "True" or "False".
- Explanation: 1-2 sentence grounding explanation.
"""

THIS_OR_THAT_TEMPLATE = """
Generate a This-or-That opinion poll for Instagram Story Poll Sticker.

Target Sport: {sport}
Retrieved Knowledge Context:
{context}

Requirements:
- Prompt: Engaging comparative question strictly between 2 iconic {sport} players, teams, or moments. Do NOT start with 'Regarding {sport}:'.
- Options: EXACTLY 2 options.
- Note: This is an opinion poll, so no single correct answer is required.
"""

FILL_IN_BLANK_TEMPLATE = """
You are a {sport} Fill-in-the-Blank quiz expert.
STRICT RULES:
1. The blank ___ MUST replace a NUMBER, PROPER NAME, YEAR, or PLACE.
   NEVER blank out verbs like won/scored/achieved/completed.
2. All 4 options must be the SAME TYPE as the blank:
   - If blank=number: all 4 options are numbers (e.g. 263.4/249.0/256.7/271.2)
   - If blank=name: all 4 options are player/venue names
   - If blank=year: all 4 options are years (e.g. 2022/2021/2023/2020)
   - If blank=place: all 4 options are location names
3. Wrong options must be PLAUSIBLE {sport} values — close but incorrect.
4. NEVER start the sentence with 'Regarding {sport}:'
   Write naturally: 'The fastest ATP serve was ___ km/h'
5. BANNED options (never use): completed, achieved, won, scored, played, finished, started, ended, happened, made, done

Facts about {sport}:
{context}

Generate one Fill-in-the-Blank question. 
This item's blank type = {blank_type}.

Requirements:
- Sentence with Blank: A sentence with '___' blank, no Regarding prefix.
- Options: EXACTLY 4 answer options of the same specific type.
- Correct Answer: The correct option text.
- Explanation: Cite the fact from context.
"""

GUESS_NUMBER_TEMPLATE = """
Generate a Guess the Number trivia challenge for Instagram.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Question: A question strictly about {sport} whose answer is a specific number. Do NOT start with 'Regarding {sport}:'.
- Target Number: A single numeric float/int value.
- Accepted Tolerance Range: A range string (e.g., "±2" or "60-65").
- Explanation: Short factual context explaining the number.
"""
