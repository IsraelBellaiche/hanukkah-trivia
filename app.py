"""Hebrew, RTL Hanukkah trivia game built with Streamlit."""

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
            radial-gradient(ellipse at 12% 8%, rgba(245, 196, 91, 0.17), transparent 34rem),
            linear-gradient(145deg, #fffdf8 0%, #f5f7fb 52%, #f8f1e8 100%);
        color: #17243b;
    }
    [data-testid="stMainBlockContainer"] {
        max-width: 860px;
        padding-top: 2.2rem;
    }
    html, body, [class*="st-"] {
        direction: rtl;
        text-align: right;
    }
    .hero-card {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        margin: 0 0 2rem;
        padding: clamp(1.7rem, 5vw, 3.2rem);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 28px;
        background: linear-gradient(128deg, #172b4d 0%, #273d68 55%, #563d69 100%);
        box-shadow: 0 22px 55px rgba(27, 40, 69, 0.2);
        color: #fff;
        direction: rtl;
        text-align: right;
        animation: hero-arrive 750ms cubic-bezier(.2, .75, .25, 1) both;
    }
    .hero-card::before {
        position: absolute;
        z-index: -1;
        top: -8rem;
        left: -5rem;
        width: 21rem;
        height: 21rem;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 205, 112, 0.3), transparent 68%);
        content: "";
        animation: glow-drift 8s ease-in-out infinite alternate;
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
        font-weight: 850;
        line-height: 1.15;
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
    .app-footer {
        direction: rtl;
        text-align: right;
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
        min-height: 3rem;
        border-radius: 14px;
        font-weight: 650;
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        border-color: #8b9bc0;
        box-shadow: 0 8px 18px rgba(35, 50, 79, 0.12);
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        border: 0;
        background: linear-gradient(110deg, #8b2f48, #aa4660);
        color: #fff;
        box-shadow: 0 8px 20px rgba(139, 47, 72, 0.22);
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

    st.title(f"שלום {st.session_state.player_name}!")
    st.progress((question_index + 1) / total_questions)
    st.caption(f"שאלה {question_index + 1} מתוך {total_questions}")
    st.subheader(question.question)

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
    st.title("כל הכבוד, סיימתם! 🕎")
    st.subheader(f"הניקוד שלכם: {score} מתוך {total_questions}")

    if not st.session_state.score_saved:
        try:
            save_score(st.session_state.player_name, score, total_questions)
        except (LeaderboardError, ValueError) as error:
            st.error(str(error))
        else:
            st.session_state.score_saved = True

    st.header("🏆 חמשת המקומות הראשונים")
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
