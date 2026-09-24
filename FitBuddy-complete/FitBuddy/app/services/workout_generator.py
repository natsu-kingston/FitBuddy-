import json
from pydantic import BaseModel, Field

from ..config import get_settings
from .gemini_client import GeminiServiceError, generate_structured


class Exercise(BaseModel):
    name: str = Field(description="Exercise name")
    sets: str = Field(description="Number of sets or a suitable set description")
    reps_or_duration: str = Field(description="Repetitions or duration")
    rest: str = Field(description="Rest interval")
    notes: str = Field(description="Short technique or safety note")


class WorkoutDay(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: list[Exercise]
    cooldown: str


class WorkoutPlan(BaseModel):
    title: str
    overview: str
    days: list[WorkoutDay]
    safety_note: str


def _demo_plan(username: str, goal: str, intensity: str) -> WorkoutPlan:
    intensity_factor = {
        "low": "easy, controlled",
        "medium": "moderate",
        "high": "challenging but controlled",
    }[intensity]

    templates = [
        ("Day 1", "Full body", ["Bodyweight squat", "Incline push-up", "Glute bridge"]),
        ("Day 2", "Cardio", ["Brisk walk", "Step-ups", "Dead bug"]),
        ("Day 3", "Upper body", ["Wall/incline push-up", "Resistance-band row", "Shoulder raise"]),
        ("Day 4", "Recovery & mobility", ["Cat-cow", "Hip flexor stretch", "Easy walk"]),
        ("Day 5", "Lower body", ["Split squat", "Hip hinge", "Calf raise"]),
        ("Day 6", "Core + cardio", ["Bird dog", "Marching plank", "Brisk walk"]),
        ("Day 7", "Active recovery", ["Easy walk", "Full-body mobility", "Breathing practice"]),
    ]

    days = []
    for day, focus, exercises in templates:
        days.append(
            WorkoutDay(
                day=day,
                focus=focus,
                warm_up="5–8 minutes of easy movement and joint mobility.",
                exercises=[
                    Exercise(
                        name=name,
                        sets="2–3",
                        reps_or_duration="8–12 reps" if "walk" not in name.lower() else "15–25 min",
                        rest="45–90 sec",
                        notes=f"Keep the effort {intensity_factor}; stop if you feel sharp pain.",
                    )
                    for name in exercises
                ],
                cooldown="5 minutes of relaxed walking and gentle stretching.",
            )
        )

    return WorkoutPlan(
        title=f"{username}'s 7-Day {goal.title()} Plan",
        overview=(
            f"A {intensity}-intensity introductory week focused on {goal}. "
            "Adjust range of motion and volume to your current ability."
        ),
        days=days,
        safety_note=(
            "This is general wellness information, not medical advice. "
            "Stop for pain, dizziness, or unusual symptoms and seek appropriate professional advice."
        ),
    )


def generate_workout_gemini(
    *,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> WorkoutPlan:
    settings = get_settings()

    if not settings.gemini_enabled:
        return _demo_plan(username, goal, intensity)

    prompt = f"""
Create a personalized 7-day fitness plan for:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Preferred intensity: {intensity}

Requirements:
1. Return exactly 7 days.
2. Each day needs a focus, 5–10 minute warm-up, exercises with sets/reps or duration/rest,
   and a cooldown/recovery instruction.
3. Vary the training across the week and include sensible recovery.
4. Do not prescribe medication, diagnose conditions, or provide extreme dieting advice.
5. Avoid pretending to know the user's training history or medical status.
6. Keep the plan practical for a general adult user.
7. Return only data matching the requested structured schema.
"""

    system = (
        "You are FitBuddy's fitness planning engine. Generate conservative, practical "
        "general-wellness exercise guidance. Personalize to the provided goal and intensity "
        "without making medical claims."
    )

    try:
        return generate_structured(
            model=settings.workout_model,
            prompt=prompt,
            response_schema=WorkoutPlan,
            system_instruction=system,
            temperature=0.5,
            max_output_tokens=7000,
        )
    except GeminiServiceError:
        # A controlled fallback keeps the application usable if a model is unavailable.
        return _demo_plan(username, goal, intensity)
