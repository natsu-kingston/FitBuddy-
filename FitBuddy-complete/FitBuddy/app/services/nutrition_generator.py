from ..config import get_settings
from .gemini_client import GeminiServiceError, generate_text


def _demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Prioritize vegetables, adequate protein, water, and minimally processed foods; avoid aggressive calorie restriction.",
        "muscle gain": "Include a protein-rich food at regular meals and eat enough overall to support training and recovery.",
        "general wellness": "Build meals around vegetables or fruit, a protein source, whole-food carbohydrates, and healthy fats.",
        "flexibility": "Stay hydrated and include balanced meals with enough protein and micronutrient-rich foods to support recovery.",
    }
    return tips.get(goal, tips["general wellness"])


def generate_nutrition_tip_with_flash(*, goal: str, age: int, weight: float) -> str:
    settings = get_settings()

    if not settings.gemini_enabled:
        return _demo_tip(goal)

    prompt = f"""
Give one concise nutrition or recovery tip for a general wellness user.
Goal: {goal}
Age: {age}
Weight: {weight} kg

Keep it to 2–4 sentences. Avoid individualized medical nutrition prescriptions,
supplement dosing, eating-disorder content, or claims that a single food guarantees a result.
"""

    try:
        return generate_text(
            model=settings.tip_model,
            prompt=prompt,
            system_instruction=(
                "You provide concise, practical general wellness nutrition and recovery tips. "
                "Do not diagnose or prescribe."
            ),
            temperature=0.4,
            max_output_tokens=300,
        )
    except GeminiServiceError:
        return _demo_tip(goal)
