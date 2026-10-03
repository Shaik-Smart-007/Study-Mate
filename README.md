# 📚 StudyMate

### From study material to mastery in minutes.

StudyMate is an AI-powered study assistant that turns study material into an **active learning loop** instead of stopping at a simple AI-generated answer.

> **Understand → Revise → Practice → Diagnose → Practice Again**

Built with **Python, Streamlit, Gemma 4, and the Gemini API**.

---

## 🚀 What is StudyMate?

Most AI study tools are built around a simple interaction:

**Ask a question → Get an answer**

StudyMate goes one step further.

It helps students:

* understand a topic,
* create concise revision notes,
* test their knowledge,
* identify weak areas,
* and practice those weak areas again.

The goal is to make AI useful as a **learning companion**, not just an answer generator.

---

## ✨ Features

### 🧠 Explain

Enter a topic, question, or study material and get a beginner-friendly explanation.

StudyMate structures explanations into:

* Simple explanation
* Key concepts
* Example or analogy when useful

---

### 📝 Revise

Turn study material into concise exam-oriented revision notes.

StudyMate organizes the response into:

* Key concepts
* Definitions, formulas and facts when present
* Common confusions when supported by the material
* 30-second recap

---

### 🎯 Quiz

Generate a multiple-choice quiz from the provided study material.

Each question includes:

* 4 answer choices
* One correct answer
* Topic identification
* Short explanation

Students answer directly inside the Streamlit interface and receive their score after submission.

---

### 📊 Weak-Area Detection

StudyMate doesn't stop after showing a score.

When a student gets questions wrong, the application identifies the topics associated with those mistakes.

For example:

```text
Score: 3 / 5

Weak areas:
• Normalization
• Functional Dependencies
```

---

### 🔄 Targeted Practice

Students can select:

**Practice weak areas**

StudyMate then asks Gemma 4 to generate **new questions specifically targeting the weak topics**.

This creates the core learning loop:

```text
Study Material
      ↓
   Explain
      ↓
    Revise
      ↓
     Quiz
      ↓
    Score
      ↓
Identify Weak Areas
      ↓
Targeted Practice
      ↓
     Quiz Again
```

---

### ⏱️ Study Plan

Students can select the amount of time they have available and generate a study plan for the current material.

Supported study durations include:

**15, 30, 45, 60, 90, and 120 minutes**

The plan uses four study phases:

1. Learn
2. Revise
3. Quiz
4. Weak-area review

---

### 📸 Optional Image Input

Text is the primary input, but students can also upload:

* textbook pages,
* handwritten notes,
* diagrams,
* or other study images.

Images are processed before being sent to Gemma 4, including orientation correction, resizing, and conversion to a consistent format.

---

## 🧩 Why StudyMate?

StudyMate is designed around a simple idea:

> **Learning should not end when the AI gives you an answer.**

Instead of only generating information, StudyMate creates a loop where the student can:

**Learn → Test → Discover Weaknesses → Practice → Test Again**

This makes the application more than a traditional conversational AI interface.

---

## 🤖 AI & Technology

### Gemma 4

StudyMate uses:

```text
gemma-4-26b-a4b-it
```

through the **Google GenAI Python SDK and Gemini API**.

Gemma 4 is used for:

* explanations,
* revision notes,
* quiz generation,
* study plans,
* weak-area practice,
* and multimodal study-material understanding.

### Technology Stack

| Technology       | Purpose                                       |
| ---------------- | --------------------------------------------- |
| Python           | Core application logic                        |
| Streamlit        | User interface                                |
| Gemma 4          | AI generation                                 |
| Gemini API       | Model access                                  |
| Google GenAI SDK | API integration                               |
| Pillow           | Image processing                              |
| python-dotenv    | Environment configuration                     |
| Git & GitHub     | Version control and open-source collaboration |

---

## 🏗️ Project Structure

```text
StudyMate/
│
├── app.py
├── gemma.py
├── prompts.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

### `app.py`

Handles:

* Streamlit UI
* User input
* Mode selection
* Quiz interaction
* Quiz scoring
* Weak-area detection
* Targeted practice flow
* Session state

### `gemma.py`

Handles communication with Gemma 4 through the Gemini API.

It includes:

* API client setup
* Gemma requests
* image preparation
* error handling
* quiz response parsing

### `prompts.py`

Contains the prompt templates used for:

* Explain
* Revise
* Quiz
* Study Plan
* Weak-area practice

Keeping prompts separate makes the AI behavior easier to maintain and improve.
