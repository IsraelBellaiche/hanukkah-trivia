import base64
import os
from pathlib import Path
import random
import time
from typing import List, Literal

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field
import streamlit as st
from score_manager import get_top_scores, save_score

CREATOR = "טריוויה מאת המכבי ישראל בלעיש"
st.set_page_config(page_title="טריוויה לחנוכה - ישראל בלעיש", page_icon="🕎", layout="centered")


class HanukkahQuestion(BaseModel):
    question: str = Field(description="שאלת טריוויה תורנית על חג החנוכה בעברית")
    options: List[str] = Field(description="ארבע אפשרויות תשובה בעברית")
    correct_answer: str = Field(description="התשובה הנכונה מתוך האפשרויות")
    fun_fact: str = Field(description="פנינה תורנית קצרה בעברית")


class HanukkahQuestionSet(BaseModel):
    questions: List[HanukkahQuestion]


BANK = {
    "קל": [
        HanukkahQuestion(
            question="כמה נרות מדליקים בלילה השמיני של חנוכה (כולל השמש)?",
            options=["8 נרות", "9 נרות", "7 נרות", "10 נרות"],
            correct_answer="9 נרות",
            fun_fact="מדליקים שמונה נרות כנגד ימי הנס ועוד נר אחד המשמש כשמש.",
        ),
        HanukkahQuestion(
            question="מהן האותיות החרוטות על הסביבון בארץ ישראל?",
            options=["נ, ג, ה, ש", "נ, ג, ה, פ", "ח, נ, ו, כ", "א, ב, ג, ד"],
            correct_answer="נ, ג, ה, פ",
            fun_fact="בארץ ישראל האותיות מסמלות נס גדול היה פה.",
        ),
        HanukkahQuestion(
            question="באיזה תאריך עברי מתחיל חג החנוכה?",
            options=["25 בכסלו", "15 בשבט", "14 באדר", "1 בתשרי"],
            correct_answer="25 בכסלו",
            fun_fact="ביום 25 בכסלו נחו החשמונאים מאויביהם וטיהרו את בית המקדש.",
        ),
        HanukkahQuestion(
            question="באיזה צד מניחים את הנרות ומאיזה צד מדליקים?",
            options=["מניחים מימין ומדליקים משמאל", "מניחים משמאל ומדליקים מימין", "מניחים ומדליקים מימין", "מהאמצע לצדדים"],
            correct_answer="מניחים מימין ומדליקים משמאל",
            fun_fact="מניחים מימין לשמאל ומדליקים משמאל לימין כדי להתחיל בנר החדש.",
        ),
        HanukkahQuestion(
            question="כמה ברכות מברכים בהדלקת נרות חנוכה בלילה הראשון?",
            options=["שלוש ברכות", "שתי ברכות", "ארבע ברכות", "ברכה אחת"],
            correct_answer="שלוש ברכות",
            fun_fact="בלילה הראשון מברכים להדליק נר חנוכה, שעשה ניסים ושהחיינו.",
        ),
        HanukkahQuestion(
            question="מהו השמן המהודר ביותר להדלקת נרות חנוכה?",
            options=["שמן זית זך", "שמן שומשום", "שמן אגוזים", "שעווה"],
            correct_answer="שמן זית זך",
            fun_fact="שמן זית מובחר משום שבו נעשה הנס במנורת המקדש.",
        ),
        HanukkahQuestion(
            question="איזה הלל אומרים בתפילת שחרית בכל ימי החנוכה?",
            options=["הלל שלם בברכה", "חצי הלל בלי ברכה", "הלל הגדול", "אין אומרים הלל"],
            correct_answer="הלל שלם בברכה",
            fun_fact="בכל שמונת ימי החנוכה גומרים את ההלל בברכה.",
        ),
        HanukkahQuestion(
            question="איזה מאכל נהוג לאכול בחנוכה זכר לנס פך השמן?",
            options=["סופגניות ולביבות", "אוזני המן", "חרוסת", "קרפלך"],
            correct_answer="סופגניות ולביבות",
            fun_fact="אוכלים מאכלים מטוגנים בשמן לזכר נס פך השמן.",
        ),
    ],
    "בינוני": [
        HanukkahQuestion(
            question="כמה זמן לפחות צריכים נרות החנוכה לדלוק?",
            options=["חצי שעה לפחות", "שעה שלמה", "רבע שעה", "עד חצות"],
            correct_answer="חצי שעה לפחות",
            fun_fact="שיעור הדלקת הנרות הוא חצי שעה לאחר צאת הכוכבים.",
        ),
        HanukkahQuestion(
            question="מה מדליקים קודם בערב שבת חנוכה?",
            options=["נרות חנוכה ואחר כך נרות שבת", "נרות שבת ואחר כך נרות חנוכה", "אין הבדל בסדר", "רק נרות שבת"],
            correct_answer="נרות חנוכה ואחר כך נרות שבת",
            fun_fact="עם הדלקת נרות שבת מקבלים שבת ולכן מקדימים נרות חנוכה.",
        ),
        HanukkahQuestion(
            question="כמה נרות בסך הכול מדליקים בכל שמונת ימי החנוכה (כולל השמש)?",
            options=["44 נרות", "36 נרות", "40 נרות", "48 נרות"],
            correct_answer="44 נרות",
            fun_fact="36 נרות המצווה ועוד 8 נרות שמש מסתכמים ב-44 נרות.",
        ),
        HanukkahQuestion(
            question="איזו תפילה מוסיפים בעמידה ובברכת המזון בחנוכה?",
            options=["על הנסים", "יעלה ויבוא", "אבינו מלכנו", "עננו"],
            correct_answer="על הנסים",
            fun_fact="נוסח על הנסים נאמר בתפילה ובברכת המזון כל שמונת הימים.",
        ),
        HanukkahQuestion(
            question="באיזו מסכת בגמרא מופיעה הסוגיה המרכזית על חנוכה?",
            options=["מסכת שבת", "מסכת מגילה", "מסכת סוכה", "מסכת ראש השנה"],
            correct_answer="מסכת שבת",
            fun_fact="במסכת שבת דף כא עמוד ב שואלת הגמרא מאי חנוכה.",
        ),
        HanukkahQuestion(
            question="מי ששכח לומר על הנסים בעמידה ונזכר לאחר שעקר רגליו, מה דינו?",
            options=["אינו חוזר", "חוזר לראש התפילה", "חוזר לרצה", "חוזר למודים"],
            correct_answer="אינו חוזר",
            fun_fact="השוכח על הנסים אינו חוזר ויכול להוסיפו בהרחמן שבברכת המזון.",
        ),
        HanukkahQuestion(
            question="מדוע נהגו לאכול מאכלי חלב בחנוכה?",
            options=["זכר למעשה יהודית והולופרנס", "כי לא היה בשר", "זכר למן במדבר", "כמו בשבועות"],
            correct_answer="זכר למעשה יהודית והולופרנס",
            fun_fact="יהודית השקתה את שר הצבא היווני חלב להרדימו והצילה את ירושלים.",
        ),
        HanukkahQuestion(
            question="איזה פיוט מפורסם שרים מיד לאחר הדלקת הנרות?",
            options=["מעוז צור ישועתי", "לכה דודי", "אדון עולם", "יגדל אלוקים חי"],
            correct_answer="מעוז צור ישועתי",
            fun_fact="ראשי הבתים של מעוז צור יוצרים את שם המחבר: מרדכי.",
        ),
    ],
    "קשה": [
        HanukkahQuestion(
            question="באיזו מחלוקת נחלקו בית שמאי ובית הלל לגבי סדר ההדלקה?",
            options=["פוחת והולך מול מוסיף והולך", "שמן זית מול שעווה", "בפנים מול בחוץ", "ברכה לפני מול אחרי"],
            correct_answer="פוחת והולך מול מוסיף והולך",
            fun_fact="ההלכה נפסקה כבית הלל שמעלין בקודש ומוסיפין והולכין.",
        ),
        HanukkahQuestion(
            question="איזו קושיה מפורסמת שאל מרן הבית יוסף על שמונת ימי החנוכה?",
            options=["מדוע חוגגים 8 ימים הרי השמן הספיק ליום הראשון בדרך הטבע", "מדוע מדליקים בשמן זית", "מדוע אוכלים סופגניות", "מדוע מברכים שהחיינו"],
            correct_answer="מדוע חוגגים 8 ימים הרי השמן הספיק ליום הראשון בדרך הטבע",
            fun_fact="קושיית הבית יוסף זכתה למאות תירוצים בספרי האחרונים.",
        ),
        HanukkahQuestion(
            question="מה פירוש הכלל ההלכתי כבתה אין זקוק לה?",
            options=["אם הנר כבה לאחר שהודלק כראוי אין חובה להדליקו שוב", "אסור לכבות נר חנוכה", "חייבים להדליק מיד אם כבה", "מדליקים רק בחוץ"],
            correct_answer="אם הנר כבה לאחר שהודלק כראוי אין חובה להדליקו שוב",
            fun_fact="הדלקה עושה מצווה ולכן אם כבה מאליו אינו חייב לחזור ולהדליק.",
        ),
        HanukkahQuestion(
            question="כיצד נקרא היום השמיני והאחרון של חנוכה במסורת ישראל?",
            options=["זאת חנוכה", "שמיני עצרת", "אסרו חג", "חנוכת המזבח"],
            correct_answer="זאת חנוכה",
            fun_fact="על שם קריאת התורה ביום זה הפותחת במילים זאת חנוכת המזבח.",
        ),
        HanukkahQuestion(
            question="איזו פרשה בתורה קוראים בכל שמונת ימי החנוכה?",
            options=["פרשת הנשיאים בפרשת נשא", "פרשת בהעלותך", "פרשת תרומה", "פרשת ויקהל"],
            correct_answer="פרשת הנשיאים בפרשת נשא",
            fun_fact="קוראים בקורבנות הנשיאים שהקריבו לחנוכת המשכן במדבר.",
        ),
        HanukkahQuestion(
            question="מדוע נשים חייבות בהדלקת נר חנוכה אף שזו מצוות עשה שהזמן גרמא?",
            options=["שאף הן היו באותו הנס", "משום נרות שבת", "מנהג בעלמא", "רק כשאינן נשואות"],
            correct_answer="שאף הן היו באותו הנס",
            fun_fact="חזל קבעו בשבת כג שנשים חייבות שאף הן היו באותו הנס.",
        ),
    ],
}


def get_questions(n: int, diff: Literal["קל", "בינוני", "קשה"]) -> List[HanukkahQuestion]:
    key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", "")).strip()
    if key:
        client = genai.Client(api_key=key)
        prompt = f"צור {n} שאלות טריוויה על חנוכה ברמת {diff} בסגנון חרדי-תורני בעברית בלבד עם 4 אפשרויות."
        for m in ("gemini-3.8-flash", "gemini-2.5-pro"):
            try:
                res = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=HanukkahQuestionSet,
                    ),
                )
                if res.parsed and len(res.parsed.questions) == n:
                    return res.parsed.questions
            except Exception:
                time.sleep(0.3)
    pool = BANK[diff]
    return random.sample(pool, k=min(n, len(pool)))


def render_avatar() -> None:
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = Path(f"israel.{ext}")
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            html = (
                '<div style="text-align:center;margin:14px 0;">'
                f'<img src="data:image/jpeg;base64,{b64}" '
                'style="width:125px;height:125px;object-fit:cover;border-radius:50%;border:4px solid #f59e0b;">'
                "</div>"
            )
            st.markdown(html, unsafe_allow_html=True)
            return


st.markdown(
    """
    <style>
    @import url('https://googleapis.com');
    .stApp {
        background: linear-gradient(180deg, #162b5c 0%, #0a132c 65%, #060b19 100%);
        color: #f8fafc;
        font-family: 'Heebo', sans-serif;
    }
    .block-container {
        direction: rtl;
