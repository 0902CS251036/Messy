
"""
Messy - Gemma 4 AI Integration

Uses Google's Gen AI SDK to analyze hostel mess feedback.
"""

import os
from google import genai

MODEL_NAME = "gemma-4-26b-a4b-it"


def analyze_mess_feedback(feedback):
    """Analyze student feedback using Gemma 4."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are the AI assistant for Messy,
    a smart hostel mess feedback system.

    Analyze the following student feedback:

    {feedback}

    Provide:
    1. A summary of student feedback.
    2. Common food-related complaints.
    3. Areas requiring improvement.
    4. Practical recommendations for mess management.

    Do not invent complaints or statistics.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text
