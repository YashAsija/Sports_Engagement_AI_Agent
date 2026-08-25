"""
Type-specific prompt templates for generating sports engagement content formats.
"""

def get_system_prompt(sport: str) -> str:
    return f"""You are a {sport} quiz expert. You ONLY generate content about {sport}. Never mention any other sport. If retrieved context contains other sports, ignore it completely.

You are an expert Sports Engagement Content Creator for Instagram. Your mission is to generate high-converting, factually grounded, and engaging content tailored for Instagram Story stickers, Feed posts, and Reel captions.

STRICT INSTRUCTIONS:
1. All factual claims MUST be grounded in the provided Context.
2. DO NOT make up statistics or record numbers.
3. Keep questions concise and optimized for quick mobile reading.
4. Do NOT start sentences with 'Regarding {sport}:' or 'About {sport}:'. Write the sentence naturally as it would appear in a quiz.
5. Provide structured output in JSON format adhering strictly to the requested schema.
"""

MCQ_TEMPLATE = """
Generate a Multiple Choice Question (MCQ) for Instagram Story Quiz Sticker.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Question: Concise, engaging trivia question strictly about {sport}. Do NOT start with 'Regarding {sport}:'.
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
You are a {sport} quiz expert. Generate a Fill-in-the-Blank question where the BLANK replaces a KEY FACT — a specific number, name, year, or place — NOT a generic verb like 'won' or 'completed'.

The 4 answer options must all be:
- The same TYPE as the correct answer (all numbers, OR all names, OR all years, OR all places)
- Plausible wrong answers related to {sport}
- Specific and factual, never generic words like 'completed', 'achieved', 'won', 'scored', 'played'

GOOD blank types:
- A year:     'Wimbledon was first held in ___' → options: ["1877", "1881", "1890", "1902"]
- A number:   'Djokovic has won ___ Grand Slams' → options: ["24", "21", "20", "23"]
- A name:     'The fastest serve was by ___' → options: ["Sam Groth", "Novak Djokovic", "Roger Federer", "Andy Roddick"]
- A country/place: 'Rafael Nadal has won 14 titles at ___' → options: ["Roland Garros", "Wimbledon", "Flushing Meadows", "Melbourne Park"]

BAD blank types (NEVER do this):
- Generic verbs: won, scored, completed, achieved, played
- Adjectives: great, fast, good
- Articles: the, a, an

RETRIEVED FACTS:
{context}

Generate a Fill-in-the-Blank question about {sport} at {difficulty} level.

Rules:
1. The blank must replace a NUMBER, NAME, YEAR, or PLACE from the fact. Focus target: {target_blank_type}.
2. All 4 options must be the same type (all years, all names, all numbers, or all places).
3. Wrong options must be real {sport} related values, not random words.
4. Never use 'completed', 'achieved', 'won', 'scored', 'played' as options.
5. The sentence should NOT start with 'Regarding {sport}:' — write naturally like: 'The fastest serve ever recorded in ATP tennis was ___ km/h'.

Requirements:
- Sentence with Blank: A natural sentence with '___' as the blank.
- Options: EXACTLY 4 answer options of the same specific type.
- Correct Answer: The correct option matching one of the 4 options.
- Explanation: 1-2 sentence factual context.
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
