"""
Type-specific prompt templates for generating sports engagement content formats.
"""

def get_system_prompt(sport: str) -> str:
    return f"""You are a {sport} specialist. You ONLY generate content about {sport}. Never mention any other sport. If retrieved context contains other sports, ignore it completely.

You are an expert Sports Engagement Content Creator for Instagram. Your mission is to generate high-converting, factually grounded, and engaging content tailored for Instagram Story stickers, Feed posts, and Reel captions.

STRICT INSTRUCTIONS:
1. All factual claims MUST be grounded in the provided Context.
2. DO NOT make up statistics or record numbers.
3. Keep questions concise and optimized for quick mobile reading.
4. Provide structured output in JSON format adhering strictly to the requested schema.
"""

MCQ_TEMPLATE = """
Generate a Multiple Choice Question (MCQ) for Instagram Story Quiz Sticker.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

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
- Statement: Clear factual statement strictly about {sport} that can be evaluated as strictly True or False.
- Correct Answer: "True" or "False".
- Explanation: 1-2 sentence grounding explanation.
"""

THIS_OR_THAT_TEMPLATE = """
Generate a This-or-That opinion poll for Instagram Story Poll Sticker.

Target Sport: {sport}
Retrieved Knowledge Context:
{context}

Requirements:
- Prompt: Engaging comparative question strictly between 2 iconic {sport} players, teams, or moments.
- Options: EXACTLY 2 options.
- Note: This is an opinion poll, so no single correct answer is required.
"""

FILL_IN_BLANK_TEMPLATE = """
Generate a Fill in the Blank challenge for Instagram.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Sentence with Blank: A sentence strictly about {sport} containing '___' where the target term goes.
- Options: EXACTLY 4 answer options to choose from.
- Correct Answer: The correct option text.
- Explanation: 1-2 sentence factual context.
"""

GUESS_NUMBER_TEMPLATE = """
Generate a Guess the Number trivia challenge for Instagram.

Target Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Question: A question strictly about {sport} whose answer is a specific number.
- Target Number: A single numeric float/int value.
- Accepted Tolerance Range: A range string (e.g., "±2" or "60-65").
- Explanation: Short factual context explaining the number.
"""
