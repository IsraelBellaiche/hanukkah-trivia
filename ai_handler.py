"""Generate Hebrew Hanukkah trivia using Google's Gemini API."""

import os
from typing import List, Literal

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field, ValidationError
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


class HanukkahQuestion(BaseModel):
    question: str = Field(description="שאלת טריוויה על חג החנוכה בעברית")
    options: List[str] = Field(description="ארבע אפשרויות תשובה בעברית")
    correct_answer: str = Field(description="התשובה הנכונה, בדיוק כפי שהיא מופיעה באפשרויות")
    fun_fact: str = Field(description="עובדה מעניינת וקצרה בעברית")


class HanukkahQuestionSet(BaseModel):
    questions: List[HanukkahQuestion]


class QuestionGenerationError(Exception):
    """Raised when questions cannot be generated or validated."""


def _get_api_key() -> str:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, StreamlitSecretNotFoundError):
        api_key = None
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise QuestionGenerationError(
            "לא נמצא מפתח Gemini. הגדירו GEMINI_API_KEY בקובץ secrets.toml "
            "או במשתני הסביבה."
        )
    return api_key.strip()


def generate_hanukkah_questions(
    num_questions: int, difficulty: Literal["קל", "בינוני", "קשה"]
) -> List[HanukkahQuestion]:
    """Generate validated Hebrew Hanukkah questions at the requested difficulty."""
    if num_questions not in (1, 5, 10):
        raise ValueError("מספר השאלות חייב להיות 1, 5 או 10.")
    if difficulty not in ("קל", "בינוני", "קשה"):
        raise ValueError("רמת הקושי חייבת להיות קל, בינוני או קשה.")

    prompt = f"""
צור בדיוק {num_questions} שאלות טריוויה מקוריות על חג החנוכה.
רמת הקושי: {difficulty}.
כתוב את כל השאלות, האפשרויות, התשובות והעובדות המעניינות בעברית בלבד.
לכל שאלה חייבות להיות בדיוק ארבע אפשרויות שונות, והתשובה הנכונה חייבת
להופיע ביניהן בדיוק. שמור על עובדות מדויקות, מגוונות ומתאימות לחג.
"""

    client = genai.Client(api_key=_get_api_key())
    last_error = None

    for model_name in ("gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"):
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
            if not isinstance(question_set, HanukkahQuestionSet):
                raise QuestionGenerationError(
                    "Gemini לא החזיר שאלות בפורמט הצפוי. נסו שוב."
                )
            if len(question_set.questions) != num_questions:
                raise QuestionGenerationError(
                    "Gemini החזיר מספר שאלות שונה מהמבוקש. נסו שוב."
                )
            for question in question_set.questions:
                if (
                    len(question.options) != 4
                    or len(set(question.options)) != 4
                    or question.correct_answer not in question.options
                ):
                    raise QuestionGenerationError(
                        "אחת השאלות שהתקבלו אינה כוללת ארבע אפשרויות ותשובה תקינה. נסו שוב."
                    )
            return question_set.questions
        except QuestionGenerationError as error:
            last_error = error
        except (errors.APIError, ValidationError, ValueError) as error:
            last_error = error

    raise QuestionGenerationError(
        f"שגיאה ביצירת השאלות: {last_error}"
    ) from last_error
