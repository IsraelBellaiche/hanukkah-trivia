"""Read and write the local Hanukkah trivia leaderboard."""

import json
import os
from pathlib import Path
from typing import Dict, List


LEADERBOARD_PATH = Path(__file__).with_name("leaderboard.json")


class LeaderboardError(Exception):
    """Raised when the leaderboard cannot be read or saved."""


def save_score(player_name: str, score: int, total_questions: int) -> None:
    """Add a completed game to the local leaderboard."""
    player_name = player_name.strip()
    if not player_name:
        raise ValueError("יש להזין שם שחקן.")
    if total_questions <= 0 or score < 0 or score > total_questions:
        raise ValueError("התוצאה שהוזנה אינה תקינה.")

    scores = _read_scores()
    scores.append(
        {
            "player_name": player_name,
            "score": score,
            "total_questions": total_questions,
        }
    )
    try:
        temporary_path = LEADERBOARD_PATH.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(scores, file, ensure_ascii=False, indent=2)
        os.replace(temporary_path, LEADERBOARD_PATH)
    except OSError as error:
        raise LeaderboardError("לא ניתן לשמור את טבלת המובילים.") from error


def get_top_scores(limit: int = 5) -> List[Dict[str, object]]:
    """Return the best scores, ranking by score percentage and then raw score."""
    if limit <= 0:
        raise ValueError("מספר התוצאות להצגה חייב להיות חיובי.")

    scores = _read_scores()
    scores.sort(
        key=lambda item: (
            item["score"] / item["total_questions"],
            item["score"],
        ),
        reverse=True,
    )
    return scores[:limit]


def _read_scores() -> List[Dict[str, object]]:
    if not LEADERBOARD_PATH.exists():
        return []

    try:
        with LEADERBOARD_PATH.open("r", encoding="utf-8") as file:
            scores = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise LeaderboardError("לא ניתן לקרוא את טבלת המובילים.") from error

    if not isinstance(scores, list):
        raise LeaderboardError("קובץ טבלת המובילים אינו בפורמט תקין.")

    for item in scores:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("player_name"), str)
            or not isinstance(item.get("score"), int)
            or not isinstance(item.get("total_questions"), int)
            or item["total_questions"] <= 0
            or item["score"] < 0
            or item["score"] > item["total_questions"]
        ):
            raise LeaderboardError("קובץ טבלת המובילים מכיל נתונים לא תקינים.")
    return scores
