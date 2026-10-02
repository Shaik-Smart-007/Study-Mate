import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Add it to your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemma-4-26b-a4b-it"


def ask_gemma(question: str) -> str:
    """Send a question to Gemma 4 and return the answer."""

    question = question.strip()

    if not question:
        return "Please enter a question."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=question,
        )

        if not response.text:
            return "Gemma returned an empty response."

        return response.text

    except Exception as error:
        return f"API error: {error}"