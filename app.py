import base64
from pathlib import Path
import streamlit as st
from ai_handler import QuestionGenerationError, generate_hanukkah_questions
from score_manager import LeaderboardError, get_top_scores, save_score

CREATOR = "טריוויה מאת המכבי ישראל בלעיש"
st.set_page_config(page_title="טריוויה לחנוכה - ישראל בלעיש", page_icon="🕎", layout="centered")

if Path("style.css").exists():
    st.markdown(f"<style>{Path('style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def get_avatar_tag() -> str:
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = Path(f"israel.{ext}")
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            return f'<img src="data:image/jpeg;base64,{b64}" class="avatar-img" alt="ישראל בלעיש">'
    return ""


for k, v in {"screen": "start", "name": "", "diff": "קל", "qs": [], "idx": 0, "score": 0, "ans": None, "saved": False}.items():
    st.session_state.setdefault(k, v)

if st.session_state.screen == "start":
    st.markdown(
        f'<div class="royal-card"><h1 class="royal-title">🕎 חידון חנוכה הממלכתי 🕎</h1>'
        f'{get_avatar_tag()}<div class="royal-badge">✨ {CREATOR} ✨</div>'
        f'<p style="text-align:center;color:#cbd5e1;margin-top:10px;">בחנו את ידיעותיכם בהלכות חנוכה, מנהגי החג וגבורת החשמונאים</p></div>',
        unsafe_allow_html=True,
    )
    name = st.text_input("מה שמכם?", value=st.session_state.name, placeholder="הקלידו את שמכם כאן...")
    c1, c2 = st.columns(2)
    diff = c1.selectbox("בחרו רמת קושי", ("קל", "בינוני", "קשה"))
    num = c2.selectbox("כמה שאלות לשחק?", (5, 10))
    if st.button("🔥 התחל משחק", type="primary"):
        if not name.strip():
            st.warning("נא להזין את השם שלכם לפני תחילת המשחק.")
        else:
            with st.spinner("מכינים עבורכם את השאלות..."):
                try:
                    qs = generate_hanukkah_questions(num, diff)
                    st.session_state.update({"name": name.strip(), "diff": diff, "qs": qs, "idx": 0, "score": 0, "ans": None, "saved": False, "screen": "game"})
                    st.rerun()
                except QuestionGenerationError as e:
                    st.error(str(e))

elif st.session_state.screen == "game":
    qs, idx = st.session_state.qs, st.session_state.idx
    q = qs[idx]
    st.markdown(f"### 🕎 בהצלחה, **{st.session_state.name}**! | ניקוד: **{st.session_state.score}**")
    st.progress((idx + 1) / len(qs))
    st.caption(f"שאלה {idx + 1} מתוך {len(qs)} | רמת קושי: {st.session_state.diff}")
    st.markdown(f'<div class="question-card">{q.question}</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, opt in enumerate(q.options):
        if cols[i % 2].button(opt, key=f"o-{idx}-{i}", disabled=st.session_state.ans is not None):
            st.session_state.ans = opt
            if opt == q.correct_answer:
                st.session_state.score += 1
            st.rerun()
    if st.session_state.ans is not None:
        if st.session_state.ans == q.correct_answer:
            st.success("ישראל נהנה! ישראל בלעיש מאמין בך מאוד שאתה מצליח! 🎉🕯️")
        else:
            st.error(f"לא נורא, ישראל בלעיש עדיין מאמין בך! התשובה הנכונה היא: {q.correct_answer}")
        st.info(f"💡 פנינה לחנוכה: {q.fun_fact}")
        if st.button("לשאלה הבאה ⬅️", type="primary"):
            st.session_state.idx += 1
            st.session_state.ans = None
            if st.session_state.idx >= len(qs):
                st.session_state.screen = "end"
            st.rerun()

else:
    tot, sc = len(st.session_state.qs), st.session_state.score
    st.markdown(
        f'<div class="royal-card"><h1 class="royal-title">אשריכם! סיימתם את החידון 🕎</h1>'
        f'<p style="text-align:center;font-size:1.4rem;font-weight:800;color:#fde68a;margin-top:10px;">הניקוד שלכם: {sc} מתוך {tot}</p></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.saved:
        try:
            save_score(st.session_state.name, sc, tot)
            st.session_state.saved = True
        except (LeaderboardError, ValueError):
            pass
    st.subheader("🏆 היכל התהילה - חמשת המקומות הראשונים")
    try:
        top = get_top_scores(5)
        if top:
            st.table([{"שם המשתתף": x["player_name"], "תוצאה": f'{x["score"]} מתוך {x["total_questions"]}'} for x in top])
    except LeaderboardError:
        pass
    if st.button("🔄 שחקו שוב", type="primary"):
        st.session_state.screen = "start"
        st.rerun()

st.markdown(f'<div style="text-align:center;margin-top:2.5rem;padding-top:1rem;border-top:1px solid #fbbf24;color:#cbd5e1;">🕎 {CREATOR} | חנוכה שמח ומאיר! 🕎</div>', unsafe_allow_html=True)
