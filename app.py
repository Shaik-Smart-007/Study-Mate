import streamlit as st

from backend import ask_gemma


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Gemma Q&A",
    page_icon="🤖",
    layout="centered",
)


# -----------------------------
# Header
# -----------------------------
st.title("🤖 Gemma 4 Q&A")
st.write("Ask a question and get an answer from Gemma 4.")


# -----------------------------
# Question input
# -----------------------------
question = st.text_area(
    "Your question",
    placeholder="Example: Explain recursion in simple words.",
    height=120,
)


# -----------------------------
# Ask button
# -----------------------------
if st.button("Ask Gemma", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Gemma is thinking..."):

            answer = ask_gemma(question)

        st.subheader("Answer")

        if answer.startswith("API error:"):
            st.error(answer)
        else:
            st.write(answer)


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption("Powered by Gemma 4 via the Gemini API")