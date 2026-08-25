"""
Type-specific prompt templates for generating sports engagement content formats.
"""

SYSTEM_PROMPT = """
You are an expert Sports Engagement Content Creator for Instagram. Your mission is to generate high-converting, factually grounded, and engaging sports content tailored for Instagram Story stickers, Feed posts, and Reel captions.

STRICT INSTRUCTIONS:
1. All factual claims MUST be grounded in the provided Context (Web Search results or Historical Database).
2. DO NOT make up statistics or record numbers. If context is missing, use verified historical knowledge.
3. Keep questions concise and optimized for quick mobile reading (under 120 characters where possible).
4. Provide structured output in JSON format adhering strictly to the requested schema.
"""

MCQ_TEMPLATE = """
Generate a Multiple Choice Question (MCQ) for Instagram Story Quiz Sticker.

Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Question: Concise, engaging trivia question.
- Options: EXACTLY 4 distinct options (A, B, C, D).
- Correct Answer: Must match one of the 4 options exactly.
- Explanation: 1-2 sentence grounding explanation.
"""

TRUE_FALSE_TEMPLATE = """
Generate a True / False challenge for Instagram Story.

Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Statement: Clear factual statement that can be evaluated as strictly True or False.
- Correct Answer: "True" or "False".
- Explanation: 1-2 sentence grounding explanation explaining why it is True or False.
"""

THIS_OR_THAT_TEMPLATE = """
Generate a This-or-That opinion poll for Instagram Story Poll Sticker.

Sport: {sport}
Retrieved Knowledge Context:
{context}

Requirements:
- Prompt: Engaging comparative question between 2 iconic players, teams, strategies, or moments (e.g. "Prime Messi vs Prime Ronaldo — better dribbler?").
- Options: EXACTLY 2 options.
- Note: This is an opinion poll, so no single correct answer is required.
"""

FILL_IN_BLANK_TEMPLATE = """
Generate a Fill in the Blank challenge for Instagram.

Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Sentence with Blank: A sentence containing '___' where the target term goes.
- Options: EXACTLY 4 answer options to choose from.
- Correct Answer: The correct option text.
- Explanation: 1-2 sentence factual context.
"""

GUESS_NUMBER_TEMPLATE = """
Generate a Guess the Number trivia challenge for Instagram.

Sport: {sport}
Difficulty: {difficulty}
Retrieved Knowledge Context:
{context}

Requirements:
- Question: A question whose answer is a specific number (e.g., "How many career hat-tricks has Cristiano Ronaldo scored?").
- Target Number: A single numeric float/int value.
- Accepted Tolerance Range: A range string (e.g., "±2" or "60-65").
- Explanation: Short factual context explaining the number.
"""
