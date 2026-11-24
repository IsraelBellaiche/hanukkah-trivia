"""Hebrew, RTL Hanukkah trivia game built with Streamlit."""

import html

import streamlit as st

from ai_handler import (
    QuestionGenerationError,
    generate_hanukkah_questions,
)
from score_manager import LeaderboardError, get_top_scores, save_score
from question_bank import HANUKKAH_QA

CREATOR_CREDIT = "טריוויה מאת המכבי ישראל בלעיש"


st.set_page_config(page_title="טריוויה לחנוכה", page_icon="🕎", layout="centered")
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 10% 4%, rgba(247, 195, 91, 0.2), transparent 32rem),
            radial-gradient(ellipse at 95% 45%, rgba(103, 113, 175, 0.11), transparent 30rem),
            linear-gradient(145deg, #fffdf8 0%, #f4f6fb 54%, #f8f1e8 100%);
        color: #17243b;
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 920px;
        padding: 2.4rem 1.5rem 1.5rem;
    }
    html, body, [class*="st-"] {
        direction: rtl;
        text-align: right;
        font-family: "Segoe UI", "Noto Sans Hebrew", Arial, sans-serif;
    }
    [data-testid="stMarkdownContainer"] p {
        line-height: 1.75;
    }
    .hero-card {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        margin: 0 0 1.7rem;
        padding: clamp(1.8rem, 5vw, 3.4rem);
        border: 1px solid rgba(255, 255, 255, 0.62);
        border-radius: 32px;
        background:
            linear-gradient(115deg, rgba(20, 38, 70, 0.98), rgba(41, 58, 101, 0.97) 58%, rgba(78, 53, 91, 0.98));
        box-shadow: 0 28px 70px rgba(27, 40, 69, 0.22), inset 0 1px rgba(255, 255, 255, 0.18);
        color: #fff;
        direction: rtl;
        text-align: right;
        animation: hero-arrive 850ms cubic-bezier(.2, .75, .25, 1) both;
    }
    .hero-card::before {
        position: absolute;
        z-index: -1;
        top: -9rem;
        left: -6rem;
        width: 25rem;
        height: 25rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 205, 112, 0.34), transparent 68%);
        content: "";
        animation: glow-drift 9s ease-in-out infinite alternate;
    }
    .hero-card::after {
        position: absolute;
        top: 14%;
        left: 8%;
        color: rgba(255, 224, 159, 0.72);
        content: "✦  ✧  ✦";
        font-size: 1.5rem;
        letter-spacing: 0.7rem;
        animation: sparkle 3.2s ease-in-out infinite;
    }
    .hero-icon {
        display: inline-block;
        margin-bottom: 0.7rem;
        font-size: 2.5rem;
        animation: lantern-float 3.2s ease-in-out infinite;
    }
    .hero-kicker {
        margin: 0 0 0.4rem;
        color: #f7d99a;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .hero-title {
        margin: 0;
        color: #fff;
        font-size: clamp(2.1rem, 7vw, 3.7rem);
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.035em;
    }
    .creator-credit {
        margin: 0.8rem 0 0;
        color: #dce5f5;
        font-size: 1rem;
    }
    .hero-invite {
        margin: 1.2rem 0 0.9rem;
        color: #fff;
        font-size: clamp(1.1rem, 3vw, 1.4rem);
        font-weight: 650;
    }
    .prize-pill {
        display: inline-block;
        margin-top: 0.25rem;
        padding: 0.55rem 1rem;
        border: 1px solid rgba(255, 226, 164, 0.55);
        border-radius: 999px;
        background: rgba(255, 218, 145, 0.16);
        color: #ffe4a8;
        font-weight: 750;
    }
    .start-hint {
        margin: 0 0 1.2rem;
        color: #526078;
        font-size: 1.05rem;
    }
    .game-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0 0 0.5rem;
        color: #53617a;
        font-size: 0.95rem;
        font-weight: 700;
    }
    .score-pill {
        padding: 0.45rem 0.8rem;
        border: 1px solid rgba(205, 157, 63, 0.3);
        border-radius: 999px;
        background: rgba(255, 249, 230, 0.9);
        color: #79550e;
        white-space: nowrap;
    }
    .question-card {
        position: relative;
        overflow: hidden;
        margin: 1.1rem 0 1.4rem;
        padding: clamp(1.35rem, 4vw, 2rem);
        border: 1px solid rgba(67, 82, 119, 0.12);
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(247, 248, 253, 0.94));
        box-shadow: 0 16px 38px rgba(42, 55, 87, 0.09);
        animation: card-arrive 450ms ease-out both;
    }
    .question-kicker {
        margin: 0 0 0.6rem;
        color: #8b2f48;
        font-size: 0.85rem;
        font-weight: 750;
        letter-spacing: 0.04em;
    }
    .question-text {
        margin: 0;
        color: #192844;
        font-size: clamp(1.35rem, 4vw, 1.85rem);
        font-weight: 750;
        line-height: 1.55;
    }
    .result-card {
        position: relative;
        overflow: hidden;
        margin: 0 0 1.6rem;
        padding: clamp(1.8rem, 5vw, 3rem);
        border: 1px solid rgba(255, 255, 255, 0.65);
        border-radius: 30px;
        background: linear-gradient(130deg, #172b4d, #34466f 62%, #704455);
        box-shadow: 0 24px 58px rgba(27, 40, 69, 0.2);
        color: #fff;
        text-align: center;
        animation: result-pop 700ms cubic-bezier(.2, .8, .25, 1) both;
    }
    .result-card::after {
        position: absolute;
        top: 0.8rem;
        left: 1rem;
        color: #ffe2a0;
        content: "✦  ✧  ✦";
        font-size: 1.4rem;
        letter-spacing: 0.5rem;
        animation: sparkle 2.7s ease-in-out infinite;
    }
    .result-kicker {
        margin: 0;
        color: #f7d99a;
        font-weight: 750;
    }
    .result-title {
        margin: 0.6rem 0 0;
        color: #fff;
        font-size: clamp(1.8rem, 5vw, 2.7rem);
        font-weight: 800;
    }
    .result-score {
        margin: 0.8rem 0 0;
        color: #ffe2a0;
        font-size: clamp(2.5rem, 9vw, 4.5rem);
        font-weight: 850;
        line-height: 1.1;
    }
    .result-caption {
        margin: 0.6rem 0 0;
        color: rgba(255, 255, 255, 0.86);
        font-size: 1.05rem;
    }
    .section-heading {
        margin: 1.6rem 0 0.8rem;
        color: #1b2b49;
        font-size: 1.35rem;
        font-weight: 800;
    }
    .app-footer {
        direction: rtl;
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(42, 57, 84, 0.16);
        color: #657187;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(42, 57, 84, 0.14);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.62);
    }
    [data-testid="stTextInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 14px;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
        border-color: #536da5;
        box-shadow: 0 0 0 2px rgba(83, 109, 165, 0.15);
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        text-align: right;
        min-height: 3.35rem;
        padding: 0.65rem 1rem;
        border: 1px solid rgba(49, 66, 104, 0.14);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
        color: #263650;
        font-size: 1rem;
        font-weight: 650;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-3px);
        border-color: #a7b3d0;
        background: #fff;
        box-shadow: 0 12px 24px rgba(35, 50, 79, 0.13);
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        border: 0;
        background: linear-gradient(110deg, #862b48, #ad4660);
        color: #fff;
        box-shadow: 0 10px 24px rgba(139, 47, 72, 0.25);
    }
    [data-testid="stProgressBar"] > div > div {
        border-radius: 999px;
        background: linear-gradient(90deg, #d6a649, #a23d5b);
    }
    [data-testid="stTable"] {
        overflow: hidden;
        border: 1px solid rgba(42, 57, 84, 0.12);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.78);
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(42, 57, 84, 0.14);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.62);
    }
    @keyframes hero-arrive {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes lantern-float {
        0%, 100% { transform: translateY(0) rotate(-3deg); }
        50% { transform: translateY(-7px) rotate(3deg); }
    }
    @keyframes glow-drift {
        from { transform: translate(0, 0) scale(0.94); }
        to { transform: translate(1.5rem, 1rem) scale(1.08); }
    }
    @keyframes sparkle {
        0%, 100% { opacity: 0.45; transform: scale(0.92); }
        50% { opacity: 1; transform: scale(1.08); }
    }
    @keyframes card-arrive {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes result-pop {
        0% { opacity: 0; transform: scale(0.96) translateY(10px); }
        70% { transform: scale(1.01); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
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
    st.markdown(
        f"""
        <section class="hero-card" dir="rtl">
            <div class="hero-icon" aria-hidden="true">🕎</div>
            <p class="hero-kicker">חגיגה של אור, ידע והפתעות</p>
            <h1 class="hero-title">טריוויה לחנוכה 🍩</h1>
            <p class="creator-credit">{CREATOR_CREDIT}</p>
            <p class="hero-invite">ישראל בלעיש מזמין אתכם לחידון החנוכה</p>
            <span class="prize-pill">🎁 מלווה בפרסים</span>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="start-hint" dir="rtl">בחרו את ההגדרות שלכם ובואו לבדוק כמה אתם יודעים על החג.</p>',
        unsafe_allow_html=True,
    )

    player_name = st.text_input("איך קוראים לכם?", value=st.session_state.player_name)
    difficulty = st.selectbox(
        "בחרו רמת קושי",
        ("קל", "בינוני", "קשה"),
        index=("קל", "בינוני", "קשה").index(st.session_state.difficulty),
    )
    num_questions = st.selectbox("כמה שאלות לשחק?", (5, 10))

    with st.expander(f"📚 לתרגול: {len(HANUKKAH_QA)} שאלות ותשובות על חנוכה"):
        st.caption("מאגר לעיון ולתרגול. שאלות המשחק עצמו נוצרות בנפרד.")
        qa_items = [
            f"**{index}. {question}**  \nתשובה: {answer}"
            for index, (question, answer) in enumerate(HANUKKAH_QA, start=1)
        ]
        st.markdown("\n\n".join(qa_items))

    if st.button("התחל משחק", type="primary"):
        if not player_name.strip():
            st.warning("נא להזין את השם שלכם לפני תחילת המשחק.")
            return

        with st.spinner("מכינים לכם שאלות לחנוכה..."):
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

    st.markdown(
        f"""
        <div class="game-meta" dir="rtl">
            <span>🕎 מסע החנוכה</span>
            <span class="score-pill">⭐ {st.session_state.score} נקודות</span>
        </div>
        <p class="start-hint">שאלה {question_index + 1} מתוך {total_questions}</p>
        """,
        unsafe_allow_html=True,
    )
    st.title(f"שלום {st.session_state.player_name}!")
    st.progress((question_index + 1) / total_questions)
    st.markdown(
        f"""
        <section class="question-card" dir="rtl">
            <p class="question-kicker">השאלה שלכם</p>
            <h2 class="question-text">{html.escape(question.question)}</h2>
        </section>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(2)
    for option_index, option in enumerate(question.options):
        with columns[option_index % 2]:
            answer_label = option
            if st.session_state.selected_answer is not None:
                if option == question.correct_answer:
                    answer_label = f"✓  {option}"
                elif option == st.session_state.selected_answer:
                    answer_label = f"✕  {option}"
            if st.button(
                answer_label,
                key=f"answer-{question_index}-{option_index}",
                disabled=st.session_state.selected_answer is not None,
                type=(
                    "primary"
                    if option == question.correct_answer
                    and st.session_state.selected_answer is not None
                    else "secondary"
                ),
            ):
                st.session_state.selected_answer = option
                if option == question.correct_answer:
                    st.session_state.score += 1

    selected_answer = st.session_state.selected_answer
    if selected_answer is not None:
        if selected_answer == question.correct_answer:
            st.success("נכון! כל הכבוד! 🎉")
        else:
            st.error(f"לא הפעם. התשובה הנכונה היא: {question.correct_answer}")
        st.info(f"ידעתם? {question.fun_fact}")

        if st.button("לשאלה הבאה", type="primary"):
            st.session_state.question_index += 1
            st.session_state.selected_answer = None
            if st.session_state.question_index >= total_questions:
                st.session_state.screen = "end"
            st.rerun()


def _show_end_screen() -> None:
    total_questions = len(st.session_state.questions)
    score = st.session_state.score
    st.markdown(
        f"""
        <section class="result-card" dir="rtl">
            <p class="result-kicker">🕎 המסע הושלם</p>
            <h1 class="result-title">כל הכבוד, {html.escape(st.session_state.player_name)}!</h1>
            <p class="result-score">{score}<span style="font-size: 1.4rem"> / {total_questions}</span></p>
            <p class="result-caption">תשובות נכונות — חג שמח ומלא אור!</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.score_saved:
        try:
            save_score(st.session_state.player_name, score, total_questions)
        except (LeaderboardError, ValueError) as error:
            st.error(str(error))
        else:
            st.session_state.score_saved = True

    st.markdown('<h2 class="section-heading" dir="rtl">🏆 חמשת המקומות הראשונים</h2>', unsafe_allow_html=True)
    try:
        top_scores = get_top_scores(5)
    except LeaderboardError as error:
        st.error(str(error))
        top_scores = []

    if top_scores:
        st.table(
            [
                {
                    "שם": item["player_name"],
                    "ניקוד": f'{item["score"]} מתוך {item["total_questions"]}',
                }
                for item in top_scores
            ]
        )
    else:
        st.write("עדיין אין תוצאות להצגה.")

    if st.button("שחק שוב", type="primary"):
        st.session_state.screen = "start"
        st.session_state.questions = []
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.session_state.selected_answer = None
        st.session_state.score_saved = False
        st.rerun()


_initialize_game_state()

if st.session_state.screen == "start":
    _show_start_screen()
elif st.session_state.screen == "game":
    _show_game_screen()
else:
    _show_end_screen()

st.markdown(
    f'<footer class="app-footer" dir="rtl">{CREATOR_CREDIT}</footer>',
    unsafe_allow_html=True,
)
