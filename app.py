"""Hebrew, RTL Hanukkah trivia game built with Streamlit - Luxury Royal & Gold UI."""

import base64
from pathlib import Path
import streamlit as st

from ai_handler import (
    QuestionGenerationError,
    generate_hanukkah_questions,
)
from score_manager import LeaderboardError, get_top_scores, save_score


CREATOR_CREDIT = "טריוויה מאת המכבי ישראל בלעיש"
IMAGE_FILENAME = "israel.jpg"


st.set_page_config(page_title="טריוויה לחנוכה - ישראל בלעיש", page_icon="🕎", layout="centered")


def _get_image_base64(path: str) -> str | None:
    file_path = Path(path)
    if not file_path.exists():
        for ext in ("png", "jpeg", "jpg", "webp"):
            alt = Path(f"israel.{ext}")
            if alt.exists():
                file_path = alt
                break
        else:
            return None
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")


st.markdown(
    """
    <style>
    @import url('https://googleapis.com');

    html, body, [class*="st-"], .stMarkdown, button, input, select {
        font-family: 'Heebo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* רקע מלכותי כחול עמוק עם זוהר עדין */
    .stApp {
        background: radial-gradient(circle at top center, #162b5c 0%, #0a132c 60%, #060b19 100%);
        color: #f8fafc;
    }

    /* כרטיס זכוכית מרכזי */
    .hero-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(251, 191, 36, 0.35);
        border-radius: 24px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.45), inset 0 0 20px rgba(251, 191, 36, 0.08);
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fde68a 0%, #f59e0b 50%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
        text-align: center !important;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1.1rem;
        margin-top: 8px;
        text-align: center !important;
    }

    /* תמונת הפרופיל שלך במסגרת זהב */
    .profile-wrapper {
        display: flex;
        justify-content: center;
        margin: 18px 0 12px 0;
    }

    .profile-img {
        width: 135px;
        height: 135px;
        object-fit: cover;
        border-radius: 50%;
        border: 4px solid #f59e0b;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.55);
    }

    .creator-badge {
        display: inline-block;
        background: linear-gradient(90deg, rgba(245,158,11,0.2), rgba(251,191,36,0.35), rgba(245,158,11,0.2));
        border: 1px solid rgba(251, 191, 36, 0.5);
        color: #fde68a;
        padding: 6px 18px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    /* כרטיס שאלה */
    .question-box {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-right: 6px solid #f59e0b;
        border-radius: 18px;
        padding: 22px;
        margin: 16px 0 22px 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }

    .question-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        line-height: 1.5;
    }

    /* עיצוב כפתורי תשובות */
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        border: 1px solid rgba(251, 191, 36, 0.35) !important;
        background: rgba(30, 41, 59, 0.85) !important;
        color: #f8fafc !important;
        transition: all 0.22s ease !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
        text-align: center !important;
    }

    div[data-testid="stButton"] > button:hover:not(:disabled) {
        transform: translateY(-2px);
        border-color: #fbbf24 !important;
        background: rgba(245, 158, 11, 0.22) !important;
        box-shadow: 0 8px 20px rgba(245, 158, 11, 0.25) !important;
    }

    /* כפתור ראשי (התחל משחק / לשאלה הבאה) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        border: none !important;
        font-weight: 900 !important;
        font-size: 1.15rem !important;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4) !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        transform: translateY(-2px);
    }

    /* שדות קלט */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] > div > div {
        background-color: rgba(15, 23, 42, 0.85) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(251, 191, 36, 0.4) !important;
        border-radius: 12px !important;
    }

    /* כותרת תחתונה */
    .app-footer {
        direction: rtl;
        text-align: center !important;
        margin-top: 3.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(251, 191, 36, 0.25);
        color: #94a3b8;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _initialize_game_state() -> None:
    defaults = {
        "screen": "start",
        "player_name": "",
        "difficulty": "קל",
        "questions": [],
        "question_index": 0,
        "score": 0,
        "selected_answer": None,
        "score_saved": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _show_start_screen() -> None:
    img_b64 = _get_image_base64(IMAGE_FILENAME)
    img_html = (
        f'<div class="profile-wrapper"><img src="data:image/jpeg;base64,{img_b64}" class="profile-img" alt="ישראל בלעיש"></div>'
        if img_b64
        else ""
    )

    st.markdown(
        f"""
        <div class="hero-card">
            <h1 class="hero-title">🕎 חידון חנוכה הממלכתי 🕎</h1>
            {img_html}
            <div class="creator-badge">✨ {CREATOR_CREDIT} ✨</div>
            <p class="hero-subtitle">בחנו את ידיעותיכם בהלכות חנוכה, מנהגי החג וגבורת החשמונאים</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    player_name = st.text_input("מה שמכם?", placeholder="הקלידו את שמכם כאן...", value=st.session_state.player_name)
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox(
            "רמת קושי",
            ("קל", "בינוני", "קשה"),
            index=("קל", "בינוני", "קשה").index(st.session_state.difficulty),
        )
    with col2:
        num_questions = st.selectbox("מספר שאלות", (5, 10))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔥 התחל משחק", type="primary"):
        if not player_name.strip():
            st.warning("נא להזין את השם שלכם לפני תחילת המשחק.")
            return

        with st.spinner("מכינים עבורכם את השאלות..."):
            try:
                questions = generate_hanukkah_questions(num_questions, difficulty)
            except QuestionGenerationError as error:
                st.error(str(error))
                return

        st.session_state.player_name = player_name.strip()
        st.session_state.difficulty = difficulty
        st.session_state.questions = questions
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.session_state.selected_answer = None
        st.session_state.score_saved = False
        st.session_state.screen = "game"
        st.rerun()


def _show_game_screen() -> None:
    questions = st.session_state.questions
    question_index = st.session_state.question_index
    question = questions[question_index]
    total_questions = len(questions)

    col_info1, col_info2 = st.columns([2, 1])
    with col_info1:
        st.markdown(f"### 🕎 בהצלחה, **{st.session_state.player_name}**!")
    with col_info2:
        st.markdown(f"<div style='text-align:left; color:#fbbf24; font-weight:800; font-size:1.15rem;'>ניקוד: {st.session_state.score}</div>", unsafe_allow_html=True)

    st.progress((question_index + 1) / total_questions)
    st.caption(f"שאלה {question_index + 1} מתוך {total_questions} | רמת קושי: {st.session_state.difficulty}")

    st.markdown(
        f"""
        <div class="question-box">
            <p class="question-text">{question.question}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(2)
    for option_index, option in enumerate(question.options):
        with columns[option_index % 2]:
            if st.button(
                option,
                key=f"answer-{question_index}-{option_index}",
                disabled=st.session_state.selected_answer is not None,
            ):
                st.session_state.selected_answer = option
                if option == question.correct_answer:
                    st.session_state.score += 1
                st.rerun()

    selected_answer = st.session_state.selected_answer
    if selected_answer is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if selected_answer == question.correct_answer:
            st.success("ישראל נהנה! ישראל בלעיש מאמין בך מאוד שאתה מצליח! 🎉🕯️")
        else:
            st.error(f"לא נורא, ישראל בלעיש עדיין מאמין בך! התשובה הנכונה היא: {question.correct_answer}")
        st.info(f"💡 **פנינה לחנוכה:** {question.fun_fact}")

        if st.button("לשאלה הבאה ⬅️", type="primary"):
            st.session_state.question_index += 1
            st.session_state.selected_answer = None
