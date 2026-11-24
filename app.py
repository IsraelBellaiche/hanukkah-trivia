"""Hebrew, RTL Hanukkah trivia game built with Streamlit."""

import streamlit as st

from ai_handler import (
    QuestionGenerationError,
    generate_hanukkah_questions,
)
from score_manager import LeaderboardError, get_top_scores, save_score


CREATOR_CREDIT = "טריוויה מאת המכבי ישראל בלעיש"


st.set_page_config(page_title="טריוויה לחנוכה", page_icon="🕎", layout="centered")
st.markdown(
    """
    <style>
    html, body, [class*="st-"] {
        direction: rtl;
        text-align: right;
    }
    .creator-credit {
        direction: rtl;
        text-align: right;
    }
    .app-footer {
        direction: rtl;
        text-align: right;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(128, 128, 128, 0.3);
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        text-align: right;
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
    st.title("🕎🍩 טריוויה לחנוכה 🍩🕎")
    st.markdown(
        f'<p class="creator-credit" dir="rtl">{CREATOR_CREDIT}</p>',
        unsafe_allow_html=True,
    )
    st.write("ברוכים הבאים! בדקו כמה אתם יודעים על חג החנוכה.")

    player_name = st.text_input("איך קוראים לכם?", value=st.session_state.player_name)
    difficulty = st.selectbox(
        "בחרו רמת קושי",
        ("קל", "בינוני", "קשה"),
        index=("קל", "בינוני", "קשה").index(st.session_state.difficulty),
    )
    num_questions = st.selectbox("כמה שאלות לשחק?", (5, 10))

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
            st.success("ישראל נהנה! ישראל בלעיש מאמין בך מאוד שאתה מצליח! 🎉")
        else:
            st.error(f"לא נורא, ישראל בלעיש עדיין מאמין בך! התשובה הנכונה היא: {question.correct_answer}")
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
