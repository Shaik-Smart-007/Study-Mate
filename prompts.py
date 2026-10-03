"""All prompt templates for StudySnap."""

SYSTEM = (
    "You are StudySnap, a patient and accurate tutor for school and college students. "
    "Base your answer on the student's material (text and/or an attached image). "
    "Do not invent facts that the material does not support. "
    "If the text or image is unclear or unreadable, say exactly what is unclear "
    "instead of guessing. "
    "If the student gave only a topic or question with no material, use "
    "well-established textbook knowledge. "
    "Use simple language and be concise."
)

JSON_FORMAT = (
    "Return ONLY a JSON array. No markdown fences, no text before or after it.\n"
    "Each item must look exactly like this:\n"
    '{"question": "...", "options": ["...", "...", "...", "..."], '
    '"answer_index": 0, "topic": "...", "explanation": "..."}\n'
    "Rules: exactly 4 options without A/B/C/D prefixes; exactly one correct option; "
    "answer_index is the position (0-3) of the correct option; "
    "topic is a 2-4 word concept name; explanation is 1-2 sentences."
)


def _material(text, has_image):
    parts = []
    if has_image:
        parts.append("(An image of the study material is attached. Read it carefully first.)")
    if text:
        parts.append(text)
    return "STUDENT MATERIAL:\n" + "\n\n".join(parts)


def explain_prompt(text, has_image):
    return (
        "Explain the material below for a beginner. "
        "Use exactly this Markdown structure:\n"
        "## Simple explanation\n(3-5 short sentences)\n"
        "## Key concepts\n(3-6 bullets: term, then a one-line meaning)\n"
        "## Example or analogy\n(one, only if it helps)\n\n"
        + _material(text, has_image)
    )


def revise_prompt(text, has_image):
    return (
        "Turn the material below into concise exam-revision notes. "
        "Use exactly this Markdown structure:\n"
        "## Key concepts\n"
        "## Definitions, formulas and facts\n(only if present in the material)\n"
        "## Common confusions\n(only if supported by the material)\n"
        "## 30-second recap\n(max 3 sentences)\n"
        "Keep the whole answer under 200 words.\n\n"
        + _material(text, has_image)
    )


def quiz_prompt(text, has_image, n=5):
    return (
        f"Create {n} multiple-choice questions that test understanding of the material below. "
        "Questions must be answerable from the material; if it is only a topic or question, "
        "use standard textbook knowledge. Mix easy and medium difficulty.\n\n"
        + JSON_FORMAT + "\n\n" + _material(text, has_image)
    )


def practice_prompt(text, has_image, weak_topics, missed_questions, n=3):
    missed = "\n".join(f"- {q}" for q in missed_questions)
    return (
        "A student took a quiz on the material below and struggled with these topics: "
        + ", ".join(weak_topics) + ".\n"
        "Questions they got wrong:\n" + missed + "\n\n"
        f"Create {n} NEW multiple-choice questions that practise those weak topics "
        "from a different angle. Do not repeat the wrong questions word for word.\n\n"
        + JSON_FORMAT + "\n\n" + _material(text, has_image)
    )


def plan_prompt(text, has_image, minutes):
    return (
        f"The student has {minutes} minutes to study the material below. "
        "Create a practical study plan as a Markdown list. "
        f"The minutes must add up to exactly {minutes}. "
        "Use these phases: Learn, Revise, Quiz, Weak-area review. "
        "For each phase give the minutes and one concrete action for THIS material.\n\n"
        + _material(text, has_image)
    )