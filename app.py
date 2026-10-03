"""StudySnap: Streamlit UI."""
import uuid

import streamlit as st
from PIL import UnidentifiedImageError

import prompts
from gemma import GemmaError, MODEL, ask_for_quiz, ask_gemma, key_is_set, prepare_image

MAX_CHARS = 8000
MODES = ["Explain", "Revise", "Quiz", "Study Plan"]

st.set_page_config(page_title="StudySnap", page_icon="📚", layout="centered")

st.session_state.setdefault("result", None)   # {"title", "content"} for text outputs
st.session_state.setdefault("quiz", None)     # quiz dict, see set_quiz()

st.title("📚 StudySnap")
st.caption("From study material to mastery in minutes.")

if not key_is_set():
    st.error("GEMINI_API_KEY is missing. Copy `.env.example` to `.env`, paste your key, and restart the app.")
    st.stop()


def set_quiz(questions, raw, material, kind="quiz"):
    st.session_state.quiz = {
        "id": uuid.uuid4().hex[:8],
        "kind": kind,                 # "quiz" or "practice"
        "questions": questions,
        "raw": raw,
        "material": material,         # kept so practice uses the same material
        "submitted": False,
        "answers": [],
    }


def handle_generate(text, uploaded, mode, minutes):
    text = text.strip()
    if not text and uploaded is None:
        st.warning("Type a question or topic, or upload an image, first.")
        return
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
        st.info(f"Your text was long, so only the first {MAX_CHARS} characters were used.")

    image_bytes = image_mime = None
    if uploaded is not None:
        try:
            image_bytes, image_mime = prepare_image(uploaded)
        except (UnidentifiedImageError, OSError, ValueError):
            st.error("Could not read that image. Try another PNG/JPG, or continue with text only.")
            return

    has_image = image_bytes is not None
    material = {"text": text, "image_bytes": image_bytes, "image_mime": image_mime}
    st.session_state.result = None
    st.session_state.quiz = None

    try:
        with st.spinner("Gemma 4 is working on it..."):
            if mode == "Quiz":
                questions, raw = ask_for_quiz(
                    prompts.quiz_prompt(text, has_image),
                    image_bytes,
                    image_mime,
                    expected_count=5,
                )
                set_quiz(questions, raw, material)
            else:
                if mode == "Explain":
                    prompt = prompts.explain_prompt(text, has_image)
                elif mode == "Revise":
                    prompt = prompts.revise_prompt(text, has_image)
                else:
                    prompt = prompts.plan_prompt(text, has_image, minutes)
                reply = ask_gemma(prompt, image_bytes, image_mime)
                st.session_state.result = {"title": mode, "content": reply}
    except GemmaError as e:
        st.error(str(e))


def start_practice(material, weak_topics, missed_questions):
    prompt = prompts.practice_prompt(
        material["text"], material["image_bytes"] is not None, weak_topics, missed_questions
    )
    try:
        with st.spinner("Gemma 4 is writing practice questions for your weak areas..."):
            questions, raw = ask_for_quiz(
                prompt,
                material["image_bytes"],
                material["image_mime"],
                expected_count=3,
            )
    except GemmaError as e:
        st.error(str(e))
        return
    set_quiz(questions, raw, material, kind="practice")
    st.rerun()


def render_quiz_form(quiz):
    with st.form("quiz_form"):
        for i, q in enumerate(quiz["questions"]):
            st.markdown(f"**Q{i + 1}. {q['question']}**")
            st.radio("Choose one", q["options"], index=None,
                     key=f"{quiz['id']}_q{i}", label_visibility="collapsed")
        submitted = st.form_submit_button("Submit answers", type="primary")
    if submitted:
        # Copy answers now: widget state is dropped once the form disappears.
        quiz["answers"] = [st.session_state.get(f"{quiz['id']}_q{i}")
                           for i in range(len(quiz["questions"]))]
        quiz["submitted"] = True
        st.rerun()


def render_results(quiz):
    questions, answers = quiz["questions"], quiz["answers"]
    score = 0
    weak_topics, missed = [], []

    for i, q in enumerate(questions):
        chosen = answers[i] if i < len(answers) else None
        if chosen == q["answer"]:
            score += 1
        else:
            missed.append(q["question"])
            if q["topic"] not in weak_topics:
                weak_topics.append(q["topic"])

    st.metric("Score", f"{score} / {len(questions)}")

    for i, q in enumerate(questions):
        chosen = answers[i] if i < len(answers) else None
        with st.container(border=True):
            st.markdown(f"**Q{i + 1}. {q['question']}**")
            if chosen == q["answer"]:
                st.success(f"Your answer: {chosen}")
            else:
                st.error(f"Your answer: {chosen or 'Not answered'}")
                st.info(f"Correct answer: {q['answer']}")
            st.caption(f"Topic: {q['topic']}")
            if q["explanation"]:
                st.markdown(q["explanation"])

    if weak_topics:
        st.warning("**Weak areas:** " + ", ".join(weak_topics))
        if st.button("Practice weak areas", type="primary"):
            start_practice(quiz["material"], weak_topics, missed)
    else:
        st.success("You got everything right, so there are no weak areas this round.")


def render_quiz():
    quiz = st.session_state.quiz
    st.divider()
    st.subheader("Quiz" if quiz["kind"] == "quiz" else "Weak-area practice")
    if not quiz["questions"]:
        st.error("Gemma's reply could not be turned into a quiz. Please try again.")
        with st.expander("Show Gemma's raw reply"):
            st.text(quiz["raw"])
        return
    if quiz["submitted"]:
        render_results(quiz)
    else:
        render_quiz_form(quiz)


# ---------- Page ----------
text = st.text_area("Your question, topic or notes", height=170,
                    placeholder="e.g. Explain how photosynthesis works, or paste your notes here")
uploaded = st.file_uploader("Optional: add a photo of a textbook page, notes or diagram",
                            type=["png", "jpg", "jpeg"])
if uploaded is not None:
    uploaded.seek(0)
    try:
        image_bytes, image_mime = prepare_image(uploaded)
        st.image(image_bytes, caption="Attached image", width=300)
    except Exception as error:
        st.error(f"Invalid image: {error}")
        uploaded = None
        
mode = st.radio("What do you want to do?", MODES, horizontal=True)
minutes = None
if mode == "Study Plan":
    minutes = st.select_slider("Time available (minutes)", options=[15, 30, 45, 60, 90, 120], value=30)

if st.button("Generate", type="primary"):
    handle_generate(text, uploaded, mode, minutes)

if st.session_state.result:
    st.divider()
    st.subheader(st.session_state.result["title"])
    st.markdown(st.session_state.result["content"])

if st.session_state.quiz:
    render_quiz()

st.divider()
st.caption(f"Powered by Gemma 4 (`{MODEL}`) via the Gemini API. AI can make mistakes, so check important facts.")