# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application based on the supplied project documentation. It generates personalized 7-day workout plans, nutrition/recovery tips, and feedback-based plan revisions with Google Gemini.

## What was implemented

- FastAPI web application and JSON API
- Jinja2 frontend with responsive CSS
- SQLite + SQLAlchemy persistence
- Gemini integration using the current `google-genai` SDK
- Structured Gemini JSON output validated with Pydantic
- 7-day workout generation
- Nutrition/recovery tip generation
- Feedback-based plan revision
- Admin-style all-users dashboard
- User deletion
- Health endpoint
- API error handling and validation
- Demo mode when no Gemini key is configured
- Automated tests for database, API validation, and demo-mode flows

## Important model update

The supplied document specifies Gemini 1.5 Pro and Gemini Flash. Those model names are no longer the safest production defaults. This implementation keeps the same Pro/Flash architecture concept but makes model names configurable through `.env`.

Defaults:
- Workout/revision: `gemini-3.1-pro-preview`
- Nutrition/recovery: `gemini-3.8-flash`

If your Google AI account does not have access to the preview Pro model, set `WORKOUT_MODEL=gemini-3.8-flash` in `.env`.

## Quick start

### 1. Open the project in VS Code

Open the `FitBuddy` folder.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env`.

```env
GEMINI_API_KEY=your_google_ai_studio_key
WORKOUT_MODEL=gemini-3.1-pro-preview
TIP_MODEL=gemini-3.8-flash
DEMO_MODE=false
```

You can obtain a Gemini API key from Google AI Studio.

If you leave `GEMINI_API_KEY` empty, the app automatically uses deterministic demo responses, so the entire UI/API/database can still be tested locally.

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

## API

### Generate

`POST /api/plans`

JSON:

```json
{
  "username": "Alex",
  "user_id": "alex01",
  "age": 28,
  "weight": 72,
  "goal": "muscle gain",
  "intensity": "medium"
}
```

### Update from feedback

`POST /api/plans/{user_id}/feedback`

JSON:

```json
{
  "feedback": "Add more cardio and include one additional recovery day."
}
```

### List users

`GET /api/users`

### Get one user

`GET /api/users/{user_id}`

### Delete one user

`DELETE /api/users/{user_id}`

### Health

`GET /health`

## Test

Install dependencies, then:

```bash
pytest -q
```

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       ├── gemini_client.py
│       ├── workout_generator.py
│       ├── nutrition_generator.py
│       └── plan_updater.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Notes

The application is a wellness/fitness planning tool, not a medical diagnosis or treatment system. Users with injuries, medical conditions, pregnancy, or other special circumstances should obtain appropriate professional advice before following a workout or nutrition plan.
