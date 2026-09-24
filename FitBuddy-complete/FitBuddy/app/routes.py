import json
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import UserPlan
from .schemas import FeedbackRequest, GenerationResponse, UserInput, UserPlanResponse
from .services.nutrition_generator import generate_nutrition_tip_with_flash
from .services.plan_updater import update_workout_plan
from .services.workout_generator import generate_workout_gemini

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def serialize_plan(record: UserPlan) -> UserPlanResponse:
    return UserPlanResponse(
        user_id=record.user_id,
        username=record.username,
        age=record.age,
        weight=record.weight,
        goal=record.goal,
        intensity=record.intensity,
        original_plan=record.original_plan,
        updated_plan=record.updated_plan,
        nutrition_tip=record.nutrition_tip,
        feedback=record.feedback,
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


def generate_and_save(payload: UserInput, db: Session) -> UserPlan:
    existing = db.scalar(select(UserPlan).where(UserPlan.user_id == payload.user_id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User ID '{payload.user_id}' already exists. Use feedback to revise the existing plan.",
        )

    workout = generate_workout_gemini(
        username=payload.username,
        age=payload.age,
        weight=payload.weight,
        goal=payload.goal,
        intensity=payload.intensity,
    )
    nutrition = generate_nutrition_tip_with_flash(
        goal=payload.goal,
        age=payload.age,
        weight=payload.weight,
    )

    record = UserPlan(
        user_id=payload.user_id,
        username=payload.username,
        age=payload.age,
        weight=payload.weight,
        goal=payload.goal,
        intensity=payload.intensity,
        original_plan=workout.model_dump_json(indent=2),
        nutrition_tip=nutrition,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "FitBuddy"},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        payload = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        record = generate_and_save(payload, db)
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "Your FitBuddy Plan",
                "record": record,
                "plan": json.loads(record.original_plan),
                "is_updated": False,
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"title": "FitBuddy", "error": str(exc)},
            status_code=400,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    record = db.scalar(select(UserPlan).where(UserPlan.user_id == user_id))
    if not record:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"title": "FitBuddy", "error": "User ID was not found."},
            status_code=404,
        )

    try:
        payload = FeedbackRequest(feedback=feedback)
        revised = update_workout_plan(
            username=record.username,
            age=record.age,
            goal=record.goal,
            intensity=record.intensity,
            original_plan=record.original_plan,
            feedback=payload.feedback,
        )
        record.updated_plan = revised.model_dump_json(indent=2)
        record.feedback = payload.feedback
        db.commit()
        db.refresh(record)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "Updated FitBuddy Plan",
                "record": record,
                "plan": json.loads(record.updated_plan),
                "is_updated": True,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "title": "FitBuddy",
                "record": record,
                "plan": json.loads(record.updated_plan or record.original_plan),
                "is_updated": bool(record.updated_plan),
                "error": str(exc),
            },
            status_code=400,
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(UserPlan).order_by(UserPlan.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"title": "All Users", "users": users},
    )


@router.post("/api/plans", response_model=GenerationResponse, status_code=201)
def create_plan(payload: UserInput, db: Session = Depends(get_db)):
    record = generate_and_save(payload, db)
    return GenerationResponse(
        message="Workout plan generated successfully.",
        plan=serialize_plan(record),
    )


@router.post("/api/plans/{user_id}/feedback", response_model=GenerationResponse)
def update_plan_api(
    user_id: str,
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):
    record = db.scalar(select(UserPlan).where(UserPlan.user_id == user_id))
    if not record:
        raise HTTPException(status_code=404, detail="User ID not found.")

    revised = update_workout_plan(
        username=record.username,
        age=record.age,
        goal=record.goal,
        intensity=record.intensity,
        original_plan=record.original_plan,
        feedback=payload.feedback,
    )
    record.updated_plan = revised.model_dump_json(indent=2)
    record.feedback = payload.feedback
    db.commit()
    db.refresh(record)

    return GenerationResponse(
        message="Workout plan updated successfully.",
        plan=serialize_plan(record),
    )


@router.get("/api/users", response_model=list[UserPlanResponse])
def list_users(db: Session = Depends(get_db)):
    records = db.scalars(select(UserPlan).order_by(UserPlan.created_at.desc())).all()
    return [serialize_plan(record) for record in records]


@router.get("/api/users/{user_id}", response_model=UserPlanResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    record = db.scalar(select(UserPlan).where(UserPlan.user_id == user_id))
    if not record:
        raise HTTPException(status_code=404, detail="User ID not found.")
    return serialize_plan(record)


@router.delete("/api/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    record = db.scalar(select(UserPlan).where(UserPlan.user_id == user_id))
    if not record:
        raise HTTPException(status_code=404, detail="User ID not found.")

    db.delete(record)
    db.commit()
    return {"message": f"User '{user_id}' deleted successfully."}


@router.get("/health")
def health():
    return {"status": "ok", "service": "fitbuddy"}
