
import streamlit as st
import json
import random
import time
import csv
from pathlib import Path

import pandas as pd

st.set_page_config(
    page_title="PE Studies Movement Master",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE = Path(__file__).parent
DATA = json.loads((BASE / "scenarios.json").read_text())
RESULTS_FILE = BASE / "results.csv"

MOVEMENTS = [
    "Flexion",
    "Extension",
    "Rotation",
    "Circumduction",
    "Pronation",
    "Supination",
    "Dorsiflexion",
    "Plantar Flexion",
    "Abduction",
    "Adduction",
    "Horizontal Adduction",
]

st.markdown(
    """
<style>
/* Overall app */
.stApp {
    background: #0f172a;
    color: #ffffff;
}

/* Force strong contrast */
html, body, [class*="css"], p, label, span, div {
    color: #f8fafc !important;
}

h1, h2, h3, h4 {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* Main page spacing */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #ffffff !important;
    font-weight: 700;
}

div[data-testid="stMetricValue"] {
    color: #22d3ee !important;
    font-weight: 900;
}

/* Buttons */
.stButton button {
    background: #1e293b;
    color: #ffffff !important;
    border: 1px solid #475569;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    font-size: 1.1rem;
    font-weight: 700;
}

.stButton button:hover {
    background: #0f766e;
    border-color: #14b8a6;
    color: #ffffff !important;
}

/* Primary next button feel */
button[kind="secondary"] {
    color: #ffffff !important;
}

/* Inputs */
input, textarea {
    color: #ffffff !important;
}

/* Feedback boxes */
.good {
    background: rgba(34,197,94,.18);
    border: 2px solid #22c55e;
    border-radius: 14px;
    padding: 16px;
    color: #ffffff !important;
    font-size: 1.1rem;
}

.bad {
    background: rgba(239,68,68,.18);
    border: 2px solid #ef4444;
    border-radius: 14px;
    padding: 16px;
    color: #ffffff !important;
    font-size: 1.1rem;
}

.info-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
}

.mode-pill {
    display: inline-block;
    background: #14b8a6;
    color: #042f2e !important;
    border-radius: 999px;
    padding: 6px 14px;
    font-weight: 900;
    margin-bottom: 10px;
}

.question-text {
    font-size: 2rem;
    line-height: 1.25;
    font-weight: 900;
    color: #ffffff !important;
    margin-bottom: 1rem;
}

.caption-text {
    color: #cbd5e1 !important;
    font-size: 1rem;
}

/* Reduce Streamlit faded disabled button text issue */
button:disabled, button[disabled] {
    opacity: 0.8 !important;
    color: #ffffff !important;
}

/* Mobile */
@media (max-width: 900px) {
    .question-text {
        font-size: 1.45rem;
    }
    .block-container {
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "order": random.sample(range(len(DATA)), len(DATA)),
        "idx": 0,
        "score": 0,
        "attempted": 0,
        "answered": False,
        "last_correct": None,
        "student_name": "",
        "quiz_started": False,
        "start_time": None,
        "exam_length": 20,
        "mode": "Practice",
        "current_options": [],
        "saved_this_exam": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quiz(exam_length=20):
    st.session_state.order = random.sample(range(len(DATA)), len(DATA))
    st.session_state.idx = 0
    st.session_state.score = 0
    st.session_state.attempted = 0
    st.session_state.answered = False
    st.session_state.last_correct = None
    st.session_state.start_time = time.time()
    st.session_state.exam_length = exam_length
    st.session_state.quiz_started = True
    st.session_state.current_options = []
    st.session_state.saved_this_exam = False


def answer_options(answer):
    wrong = [movement for movement in MOVEMENTS if movement != answer]
    options = [answer] + random.sample(wrong, 3)
    random.shuffle(options)
    return options


def save_result_once():
    if st.session_state.saved_this_exam:
        return

    result = {
        "timestamp": pd.Timestamp.now().isoformat(timespec="seconds"),
        "student": st.session_state.student_name.strip() or "Unknown",
        "mode": st.session_state.mode,
        "score": st.session_state.score,
        "attempted": st.session_state.attempted,
        "percent": round((st.session_state.score / max(1, st.session_state.attempted)) * 100, 1),
        "time_seconds": int(time.time() - (st.session_state.start_time or time.time())),
    }

    exists = RESULTS_FILE.exists()

    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=result.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(result)

    st.session_state.saved_this_exam = True


def current_item():
    return DATA[st.session_state.order[st.session_state.idx]]


def next_question():
    st.session_state.idx = (st.session_state.idx + 1) % len(st.session_state.order)
    st.session_state.answered = False
    st.session_state.last_correct = None
    st.session_state.current_options = []


init_state()

st.title("🏃 PE Studies Movement Master")
st.caption("Year 12 General PE Studies | Types of movement used in selected sports")

setup_left, setup_mid, setup_right = st.columns([1.2, 1, 1])

with setup_left:
    st.session_state.student_name = st.text_input(
        "Student name",
        value=st.session_state.student_name,
        placeholder="Enter your name",
    )

with setup_mid:
    st.session_state.mode = st.radio(
        "Mode",
        ["Learn", "Practice", "Exam"],
        horizontal=True,
        index=["Learn", "Practice", "Exam"].index(st.session_state.mode),
    )

with setup_right:
    exam_len = st.selectbox("Exam length", [5, 10, 15, 20, 25, 30, 40], index=3)

start_col, reset_col = st.columns([1, 5])
with start_col:
    if st.button("Start / Restart", use_container_width=True):
        reset_quiz(exam_len)

if not st.session_state.quiz_started:
    st.markdown(
        """
<div class="info-card">
    <h3>How it works</h3>
    <p>Students view a sport-specific image, read the movement question, then identify the correct movement.</p>
    <p><b>Learn Mode</b> shows the answer. <b>Practice Mode</b> gives instant feedback. <b>Exam Mode</b> records a final score.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.subheader("Movements included")
    st.write(", ".join(MOVEMENTS))
    st.stop()

# End exam
if st.session_state.mode == "Exam" and st.session_state.attempted >= st.session_state.exam_length:
    save_result_once()
    st.success(f"Exam complete: {st.session_state.score}/{st.session_state.attempted}")

    if st.button("Start another exam", use_container_width=True):
        reset_quiz(exam_len)
        st.rerun()

    st.stop()

item = current_item()

m1, m2, m3 = st.columns(3)
m1.metric("Question", f"{st.session_state.attempted + 1}" if st.session_state.mode == "Exam" else st.session_state.idx + 1)
m2.metric("Score", f"{st.session_state.score}/{st.session_state.attempted}")
m3.metric("Time", f"{int(time.time() - st.session_state.start_time)}s" if st.session_state.start_time else "0s")

st.write("")

left, right = st.columns([1.35, 1], gap="large")

with left:
    img_path = BASE / item["image"]

    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.error(f"Missing image: {item['image']}")

    st.markdown(
        f"<p class='caption-text'>Scenario: <b>{item['title']}</b> | Question focus: <b>{item['focus']}</b></p>",
        unsafe_allow_html=True,
    )

with right:
    st.markdown(f"<span class='mode-pill'>{st.session_state.mode} Mode</span>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-text'>{item['question']}</div>", unsafe_allow_html=True)

    if st.session_state.mode == "Learn":
        st.markdown(f"### Answer: :green[{item['answer']}]")
        st.write(item["explanation"])

    else:
        if not st.session_state.current_options:
            st.session_state.current_options = answer_options(item["answer"])

        for option in st.session_state.current_options:
            button_label = option

            if st.session_state.answered and option == item["answer"]:
                button_label = f"✅ {option}"

            if st.button(
                button_label,
                key=f"{st.session_state.idx}_{option}",
                disabled=st.session_state.answered,
                use_container_width=True,
            ):
                st.session_state.answered = True
                st.session_state.attempted += 1

                if option == item["answer"]:
                    st.session_state.score += 1
                    st.session_state.last_correct = True
                else:
                    st.session_state.last_correct = False

                st.rerun()

        if st.session_state.answered:
            if st.session_state.last_correct:
                st.markdown(
                    f"<div class='good'><b>✅ Correct.</b><br>{item['explanation']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='bad'><b>❌ Not quite. Correct answer: {item['answer']}.</b><br>{item['explanation']}</div>",
                    unsafe_allow_html=True,
                )

    if st.button("Next question →", use_container_width=True):
        next_question()
        st.rerun()

st.divider()

with st.expander("Scenario bank"):
    cols = st.columns(4)

    for i, scenario in enumerate(DATA):
        with cols[i % 4]:
            path = BASE / scenario["image"]

            if path.exists():
                st.image(str(path), use_container_width=True)

            st.markdown(f"**{i + 1}. {scenario['title']}**")
            st.caption(f"{scenario['focus']}")

with st.expander("Teacher results dashboard"):
    if RESULTS_FILE.exists():
        df = pd.read_csv(RESULTS_FILE)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download results CSV",
            df.to_csv(index=False),
            "movement_master_results.csv",
            "text/csv",
        )
    else:
        st.write("No saved results yet. Results save when an Exam finishes.")
