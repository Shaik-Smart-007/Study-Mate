"""Everything that talks to Gemma 4 through the Gemini API."""
import io
import json
import os
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageOps

from prompts import SYSTEM

load_dotenv()

MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
THINKING_LEVEL = "minimal"   # documented values: "minimal" (off) / "high" (on). None = don't send.
MAX_IMAGE_SIDE = 1600

_client = None


class GemmaError(Exception):
    """Friendly, user-facing error."""


def key_is_set():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(key) and key != "paste_your_key_here"


def get_client():
    global _client
    if not key_is_set():
        raise GemmaError("GEMINI_API_KEY is missing. Add it to your .env file and restart.")
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY").strip())
    return _client


def prepare_image(uploaded_file):
    """Fix rotation, shrink big photos, return (jpeg_bytes, mime_type)."""
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg"


def ask_gemma(prompt, image_bytes=None, image_mime=None):
    """Send prompt (+ optional image) to Gemma 4, return the reply text."""
    client = get_client()

    contents = []
    if image_bytes:
        # Gemma docs recommend putting the image before the text.
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime))
    contents.append(prompt)

    config_args = {"system_instruction": SYSTEM}
    if THINKING_LEVEL:
        config_args["thinking_config"] = types.ThinkingConfig(thinking_level=THINKING_LEVEL)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(**config_args),
        )
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            raise GemmaError("Rate limit reached. Wait a few seconds and try again.") from e
        if "API key" in msg or "API_KEY" in msg or "401" in msg or "403" in msg:
            raise GemmaError("The API key was rejected. Check GEMINI_API_KEY in your .env file.") from e
        raise GemmaError(f"Gemma API error: {msg[:300]}") from e

    text = (response.text or "").strip()
    if not text:
        raise GemmaError("Gemma returned an empty reply. Please try again.")
    return text


# ---------- Quiz parsing ----------

def _extract_json_list(text):
    """Grab the outermost [...] from the reply, ignoring fences or chatter."""
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def parse_quiz(text):
    """Return a list of valid questions (possibly empty). Never raises."""
    data = _extract_json_list(text)
    if not isinstance(data, list):
        return []
    questions = []
    for item in data:
        try:
            question = item["question"]
            options_value = item["options"]
            answer_index = item["answer_index"]
            if (
                not isinstance(question, str)
                or not question.strip()
                or not isinstance(options_value, list)
                or len(options_value) != 4
                or not all(isinstance(option, str) and option.strip() for option in options_value)
                or type(answer_index) is not int
                or not 0 <= answer_index <= 3
            ):
                continue
            question = question.strip()
            options = [option.strip() for option in options_value]
            if len(set(options)) != 4:
                continue
            correct = options[answer_index]
            random.shuffle(options)  # models love putting answers in the same slot
            questions.append({
                "question": question,
                "options": options,
                "answer": correct,
                "topic": str(item.get("topic", "")).strip() or "General",
                "explanation": str(item.get("explanation", "")).strip(),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return questions


def ask_for_quiz(prompt, image_bytes=None, image_mime=None, expected_count=5):
    """Ask Gemma for a quiz; retry once if the JSON is unusable.
    Returns (questions, raw_text). questions is [] if both tries failed."""
    raw = ""
    for attempt in range(2):
        request = prompt
        if attempt == 1:
            request += (
                "\n\nYour previous response was invalid. Return ONLY a valid JSON array "
                f"with exactly {expected_count} valid questions. No markdown or text outside JSON. "
                "Every question must have exactly four unique non-empty options and one valid "
                "answer_index."
            )
        raw = ask_gemma(request, image_bytes, image_mime)
        questions = parse_quiz(raw)
        if len(questions) >= expected_count:
            return questions[:expected_count], raw
    return [], raw