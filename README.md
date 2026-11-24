# טריוויה לחנוכה

משחק טריוויה בעברית עם שאלות שנוצרות באמצעות Gemini, ממשק RTL וטבלת
מובילים מקומית.

## התקנה והפעלה

1. התקינו Python 3.9 ומעלה.
2. התקינו את החבילות:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. הגדירו מפתח API באחת מהדרכים הבאות:
   - צרו `.streamlit/secrets.toml` והוסיפו `GEMINI_API_KEY = "המפתח_שלכם"`.
   - לחלופין, הגדירו משתנה סביבה בשם `GEMINI_API_KEY`.
4. הפעילו את המשחק מתוך התיקייה:

   ```powershell
   streamlit run app.py
   ```

התוצאות נשמרות בקובץ `leaderboard.json` לצד קובצי המשחק.
