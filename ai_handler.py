import os
import random
import time
from typing import List, Literal, Optional

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field, ValidationError
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


class HanukkahQuestion(BaseModel):
    question: str = Field(description="שאלת טריוויה על חג החנוכה בעברית")
    options: List[str] = Field(description="ארבע אפשרויות תשובה בעברית")
    correct_answer: str = Field(description="התשובה הנכונה מתוך האפשרויות")
    fun_fact: str = Field(description="עובדה מעניינת וקצרה בעברית")


class HanukkahQuestionSet(BaseModel):
    questions: List[HanukkahQuestion]


class QuestionGenerationError(Exception):
    pass


FALLBACK_QUESTIONS = {
    "קל": [
        HanukkahQuestion(
            question="כמה נרות מדליקים בחנוכייה ביום השמיני של חנוכה (כולל השמש)?",
            options=["8 נרות", "9 נרות", "7 נרות", "10 נרות"],
            correct_answer="9 נרות",
            fun_fact="ביום השמיני מדליקים 8 נרות כנגד ימי החג, ועוד נר אחד נוסף המשמש כשמש.",
        ),
        HanukkahQuestion(
            question="איזה מאכל מסורתי נהוג לאכול בחנוכה זכר לנס פך השמן?",
            options=["אוזני המן", "סופגנייה", "חרוסת", "קרפלך"],
            correct_answer="סופגנייה",
            fun_fact="מאכלים המטוגנים בשמן עמוק מזכירים את פך השמן שהספיק לשמונה ימים.",
        ),
        HanukkahQuestion(
            question="מהן האותיות המופיעות על הסביבון בישראל?",
            options=["נ, ג, ה, ש", "נ, ג, ה, פ", "ח, נ, ו, כ", "א, ב, ג, ד"],
            correct_answer="נ, ג, ה, פ",
            fun_fact="בישראל האותיות מסמלות נס גדול היה פה, ובחוץ לארץ מופיעה האות ש.",
        ),
        HanukkahQuestion(
            question="באיזה תאריך עברי מתחיל חג החנוכה?",
            options=["25 בכסלו", "15 בשבט", "14 באדר", "1 בתשרי"],
            correct_answer="25 בכסלו",
            fun_fact="ביום 25 בכסלו נחו החשמונאים מאויביהם וטיהרו את בית המקדש.",
        ),
        HanukkahQuestion(
            question="מי הוביל את מרד החשמונאים בתחילתו?",
            options=["מתתיהו ובניו", "שמשון הגיבור", "דוד המלך", "בר כוכבא"],
            correct_answer="מתתיהו ובניו",
            fun_fact="מתתיהו הכהן מהעיר מודיעין החל את המרד, ואחריו הנהיג אותו בנו יהודה המכבי.",
        ),
    ],
    "בינוני": [
        HanukkahQuestion(
            question="איזו אימפריה שלטה בארץ ישראל בתקופת מרד החשמונאים?",
            options=["האימפריה הסלאוקית", "האימפריה הרומית", "האימפריה הבבלית", "האימפריה הפרסית"],
            correct_answer="האימפריה הסלאוקית",
            fun_fact="הסלאוקים היו יורשיו של אלכסנדר מוקדון ששלטו בסוריה ובארץ ישראל.",
        ),
        HanukkahQuestion(
            question="מה היה שמו של מלך יוון שגזר גזירות שמד על היהודים?",
            options=["אנטיוכוס הרביעי", "אלכסנדר מוקדון", "טיטוס", "נבוכדנצר"],
            correct_answer="אנטיוכוס הרביעי",
            fun_fact="אנטיוכוס כינה את עצמו אפיפנס, אך מתנגדיו כינו אותו בלעג אפימנס (המשוגע).",
        ),
        HanukkahQuestion(
            question="באיזו עיר פרץ מרד החשמונאים?",
            options=["מודיעין", "ירושלים", "צפת", "חברון"],
            correct_answer="מודיעין",
            fun_fact="במודיעין סירב מתתיהו להקריב קורבן לאלילים והחל את המרד.",
        ),
        HanukkahQuestion(
            question="איזו תפילה מיוחדת מוסיפים בתפילת העמידה ובברכת המזון בחנוכה?",
            options=["על הנסים", "יעלה ויבוא", "אבינו מלכנו", "נשמת כל חי"],
            correct_answer="על הנסים",
            fun_fact="תפילת על הנסים נאמרת רק בשני חגים: חנוכה ופורים.",
        ),
        HanukkahQuestion(
            question="כמה נרות בסך הכול מדליקים במהלך כל שמונת ימי החנוכה (כולל השמש)?",
            options=["44 נרות", "36 נרות", "40 נרות", "48 נרות"],
            correct_answer="44 נרות",
            fun_fact="36 נרות המצווה ועוד 8 נרות שמש מסתכמים יחד ב-44 נרות.",
        ),
    ],
    "קשה": [
        HanukkahQuestion(
            question="מה היה שמו המקורי של הכהן הגדול המתייוון יאסון?",
            options=["יהושע", "מנלאוס", "אלקימוס", "חוניו"],
            correct_answer="יהושע",
            fun_fact="יהושע שינה את שמו לשם היווני יאסון והקים בירושלים גימנסיון.",
        ),
        HanukkahQuestion(
            question="באיזו שנה לפני הספירה טוהר בית המקדש בידי יהודה המכבי?",
            options=["164 לפנהס", "167 לפנהס", "142 לפנהס", "63 לפנהס"],
            correct_answer="164 לפנהס",
            fun_fact="המרד פרץ ב-167 לפנהס ולאחר כשלוש שנים טוהר בית המקדש.",
        ),
        HanukkahQuestion(
            question="איזה אח מבין החשמונאים נהרג בקרב בית זכריה כשדקר פיל מלחמה מלמטה?",
            options=["אלעזר החורני", "שמעון התרסי", "יוחנן הגדי", "יונתן הוופסי"],
            correct_answer="אלעזר החורני",
            fun_fact="אלעזר חשב שהמלך אנטיוכוס רוכב על הפיל המשוריין וזחל תחתיו.",
        ),
        HanukkahQuestion(
            question="מה היה כינויו של שמעון, בנו של מתתיהו שהפך לנשיא וכהן גדול?",
            options=["התרסי", "המכבי", "הגדי", "הוופסי"],
            correct_answer="התרסי",
            fun_fact="שמעון התרסי ביסס את עצמאות ממלכת החשמונאים.",
        ),
        HanukkahQuestion(
            question="איזה שמן נחשב למובחר ביותר להדלקת נרות חנוכה על פי ההלכה?",
            options=["שמן זית זך", "שמן שומשום", "שמן קיק", "שמן אגוזים"],
            correct_answer="שמן זית זך",
            fun_fact="שמן זית מועדף משום שבו נעשה הנס במקדש ומשום שאורו צלול ויציב.",
        ),
    ],
}


def _get_api_key() -> Optional[str]:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, StreamlitSecretNotFoundError):
        api_key = None
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
    return api_key.strip() if api_key else None


def _get_fallback_questions(
    num_questions: int, difficulty: Literal["קל", "בינוני", "קשה"]
) -> List[HanukkahQuestion]:
    pool = FALLBACK_QUESTIONS[difficulty]
    if num_questions <= len(pool):
        return random.sample(pool, k=num_questions)
    return random.choices(pool, k=num_questions)


def generate_hanukkah_questions(
    num_questions: int, difficulty: Literal["קל", "בינוני", "קשה"]
) -> List[HanukkahQuestion]:
    if num_questions not in (1, 5, 10):
        raise ValueError("מספר השאלות חייב להיות 1, 5 או 10.")
    if difficulty not in ("קל", "בינוני", "קשה"):
        raise ValueError("רמת הקושי חייבת להיות קל, בינוני או קשה.")

    api_key = _get_api_key()
    if not api_key:
        return _get_fallback_questions(num_questions, difficulty)

    prompt = (
        f"צור בדיוק {num_questions} שאלות טריוויה מקוריות על חג החנוכה "
        f"ברמת קושי {difficulty}. כתוב הכל בעברית בלבד, עם 4 אפשרויות שונות לכל שאלה."
    )

    client = genai.Client(api_key=api_key)

    for model_name in ("gemini-3.8-flash", "gemini-2.5-pro"):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=HanukkahQuestionSet,
                ),
            )
            question_set = response.parsed
            if (
                isinstance(question_set, HanukkahQuestionSet)
                and len(question_set.questions) == num_questions
                and all(
                    len(q.options) == 4
                    and len(set(q.options)) == 4
                    and q.correct_answer in q.options
                    for q in question_set.questions
                )
            ):
                return question_set.questions
        except (errors.APIError, ValidationError, ValueError):
            time.sleep(0.5)

    return _get_fallback_questions(num_questions, difficulty)
