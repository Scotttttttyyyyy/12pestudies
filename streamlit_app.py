
import streamlit as st
import json, random, time, csv
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="PE Studies Movement Master", page_icon="🏃", layout="wide")

BASE = Path(__file__).parent
DATA = json.loads((BASE / "scenarios.json").read_text())
MOVEMENTS = ["Flexion","Extension","Rotation","Circumduction","Pronation","Supination","Dorsiflexion","Plantar Flexion","Abduction","Adduction","Horizontal Adduction"]
RESULTS_FILE = BASE / "results.csv"

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#0b1220,#0f172a); }
div[data-testid="stMetricValue"] { color: #14b8a6; }
.good {background:rgba(34,197,94,.15);border:1px solid #22c55e;border-radius:12px;padding:12px;}
.bad {background:rgba(239,68,68,.15);border:1px solid #ef4444;border-radius:12px;padding:12px;}
</style>
""", unsafe_allow_html=True)

def init_state():
    defaults = {
        "order": random.sample(range(len(DATA)), len(DATA)),
        "idx": 0, "score": 0, "attempted": 0, "answered": False,
        "last_correct": None, "student_name": "", "quiz_started": False,
        "start_time": None, "exam_length": 20, "mode": "Practice",
        "current_options": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

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

def answer_options(answer):
    wrong = [m for m in MOVEMENTS if m != answer]
    opts = [answer] + random.sample(wrong, 3)
    random.shuffle(opts)
    return opts

def save_result():
    item = {
        "timestamp": pd.Timestamp.now().isoformat(timespec="seconds"),
        "student": st.session_state.student_name.strip() or "Unknown",
        "mode": st.session_state.mode,
        "score": st.session_state.score,
        "attempted": st.session_state.attempted,
        "percent": round((st.session_state.score / max(1, st.session_state.attempted)) * 100, 1),
        "time_seconds": int(time.time() - (st.session_state.start_time or time.time()))
    }
    exists = RESULTS_FILE.exists()
    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=item.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(item)

init_state()

st.title("🏃 PE Studies Movement Master")
st.caption("Year 12 General PE Studies | Types of movement used in selected sports")

with st.sidebar:
    st.header("Student Setup")
    st.session_state.student_name = st.text_input("Student name", st.session_state.student_name)
    st.session_state.mode = st.radio("Mode", ["Learn", "Practice", "Exam"], index=["Learn","Practice","Exam"].index(st.session_state.mode))
    exam_len = st.slider("Exam length", 5, 40, st.session_state.exam_length, 5)
    if st.button("Start / Restart", use_container_width=True):
        reset_quiz(exam_len)
    st.divider()
    st.metric("Score", st.session_state.score)
    st.metric("Attempted", st.session_state.attempted)
    if st.session_state.start_time:
        st.write(f"Time: {int(time.time() - st.session_state.start_time)} seconds")

if not st.session_state.quiz_started:
    st.info("Enter a student name, choose a mode, then press **Start / Restart**.")
    st.subheader("Movements included")
    st.write(", ".join(MOVEMENTS))
    st.stop()

if st.session_state.mode == "Exam" and st.session_state.attempted >= st.session_state.exam_length:
    st.success(f"Exam complete: {st.session_state.score}/{st.session_state.attempted}")
    save_result()
    if st.button("Start another exam"):
        reset_quiz(exam_len)
    st.stop()

item = DATA[st.session_state.order[st.session_state.idx]]

m1, m2, m3 = st.columns(3)
m1.metric("Question", f"{st.session_state.attempted + 1}" if st.session_state.mode == "Exam" else st.session_state.idx + 1)
m2.metric("Score", f"{st.session_state.score}/{st.session_state.attempted}")
m3.metric("Time", f"{int(time.time() - st.session_state.start_time)}s" if st.session_state.start_time else "0s")

left, right = st.columns([1.15, 0.85], gap="large")
with left:
    img_path = BASE / item["image"]
    if img_path.exists():
        st.image(str(img_path), use_container_width=True)
    else:
        st.warning(f"Missing image: {item['image']}")
    st.caption(f"Scenario: {item['title']} | Question focus: {item['focus']}")

with right:
    st.subheader(item["question"])
    if st.session_state.mode == "Learn":
        st.markdown(f"### Answer: :green[{item['answer']}]")
        st.write(item["explanation"])
    else:
        if not st.session_state.current_options:
            st.session_state.current_options = answer_options(item["answer"])
        for option in st.session_state.current_options:
            if st.button(option, key=f"{st.session_state.idx}_{option}", disabled=st.session_state.answered, use_container_width=True):
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
                st.markdown(f"<div class='good'><b>✅ Correct.</b><br>{item['explanation']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bad'><b>❌ Not quite. Correct answer: {item['answer']}.</b><br>{item['explanation']}</div>", unsafe_allow_html=True)
    if st.button("Next question →", use_container_width=True):
        st.session_state.idx = (st.session_state.idx + 1) % len(st.session_state.order)
        st.session_state.answered = False
        st.session_state.last_correct = None
        st.session_state.current_options = []
        st.rerun()

st.divider()
with st.expander("Scenario bank"):
    cols = st.columns(4)
    for i, s in enumerate(DATA):
        with cols[i % 4]:
            img_path = BASE / s["image"]
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            st.markdown(f"**{i+1}. {s['title']}**")
            st.caption(f"{s['focus']}")

with st.expander("Teacher results dashboard"):
    if RESULTS_FILE.exists():
        df = pd.read_csv(RESULTS_FILE)
        st.dataframe(df, use_container_width=True)
        st.download_button("Download results CSV", df.to_csv(index=False), "movement_master_results.csv", "text/csv")
    else:
        st.write("No saved results yet. Results save when an Exam finishes.")
