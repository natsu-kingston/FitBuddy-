from ..config import get_settings
from .gemini_client import GeminiServiceError, generate_structured
from .workout_generator import WorkoutPlan, _demo_plan


def update_workout_plan(
    *,
    username: str,
    age: int,
    goal: str,
    intensity: str,
    original_plan: str,
    feedback: str,
) -> WorkoutPlan:
    settings = get_settings()

    if not settings.gemini_enabled:
        # Demo fallback creates a fresh plan and incorporates the feedback in the overview.
        plan = _demo_plan(username, goal, intensity)
        plan.overview += f" Demo revision applied from feedback: {feedback}"
        return plan

    prompt = f"""
Revise this existing FitBuddy 7-day plan according to the user's feedback.

User:
- Name: {username}
- Age: {age}
- Goal: {goal}
- Intensity: {intensity}

Original plan:
{original_plan}

Feedback:
{feedback}

Requirements:
- Preserve the 7-day structure.
- Make concrete changes that address the feedback.
- Keep the plan appropriate for general wellness.
- Include warm-up, exercises, rest, and cooldown for every day.
- Do not add medical diagnoses or medication advice.
- Return only data matching the structured schema.
"""

    try:
        return generate_structured(
            model=settings.workout_model,
            prompt=prompt,
            response_schema=WorkoutPlan,
            system_instruction=(
                "You are FitBuddy's plan revision engine. Respect user feedback while "
                "maintaining safe, practical general-wellness exercise guidance."
            ),
            temperature=0.5,
            max_output_tokens=7000,
        )
    except GeminiServiceError:
        plan = _demo_plan(username, goal, intensity)
        plan.overview += f" Fallback revision noted: {feedback}"
        return plan
