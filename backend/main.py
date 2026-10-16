from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from backend.config import FRONTEND_ORIGINS
from backend.database import Base, SessionLocal, engine, get_db
from backend.evaluator import evaluate_submission
from backend.models import Exercise, Submission, Track, User
from backend.schemas import HintRequest, LoginRequest, RegisterRequest, SubmissionRequest, UserResponse
from backend.security import clear_session_cookie, hash_password, require_user_id, set_session_cookie, verify_password
from backend.seed import seed_database


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
        instructor_email = os.getenv("SEED_INSTRUCTOR_EMAIL", "").strip().lower()
        instructor_password = os.getenv("SEED_INSTRUCTOR_PASSWORD", "")
        if bool(instructor_email) != bool(instructor_password):
            raise RuntimeError("Set both SEED_INSTRUCTOR_EMAIL and SEED_INSTRUCTOR_PASSWORD to provision an instructor.")
        if instructor_password and len(instructor_password) < 10:
            raise RuntimeError("SEED_INSTRUCTOR_PASSWORD must contain at least 10 characters.")
        if instructor_email:
            user = db.scalar(select(User).where(User.email == instructor_email))
            if user is None:
                db.add(User(
                    name="Platform instructor",
                    email=instructor_email,
                    password_hash=hash_password(instructor_password),
                    role="instructor",
                ))
                db.commit()
            elif user.role != "instructor":
                raise RuntimeError("SEED_INSTRUCTOR_EMAIL is already registered as a student; use a different address.")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="SkillForge API",
    description="Practical coding and industry-readiness platform",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def home():
    return {"name": "SkillForge API", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    reserved_email = os.getenv("SEED_INSTRUCTOR_EMAIL", "").strip().lower()
    if reserved_email and email == reserved_email:
        raise HTTPException(status_code=409, detail="This email is reserved for instructor provisioning.")
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        role="student",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.") from exc
    db.refresh(user)
    set_session_cookie(response, user.id)
    return user


@app.post("/api/auth/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    set_session_cookie(response, user.id)
    return user


@app.post("/api/auth/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"status": "signed_out"}


@app.get("/api/auth/me", response_model=UserResponse)
def current_user(request: Request, db: Session = Depends(get_db)):
    user = db.get(User, require_user_id(request))
    if user is None:
        raise HTTPException(status_code=401, detail="Session is no longer valid.")
    return user


@app.get("/api/tracks")
def list_tracks(db: Session = Depends(get_db)):
    tracks = db.scalars(select(Track).options(joinedload(Track.exercises)).order_by(Track.id)).unique().all()
    return [{
        "id": track.id,
        "slug": track.slug,
        "title": track.title,
        "description": track.description,
        "level": track.level,
        "icon": track.icon,
        "exercise_count": len(track.exercises),
    } for track in tracks]


def serialize_exercise(exercise: Exercise) -> dict:
    return {
        "id": exercise.id,
        "slug": exercise.slug,
        "track_id": exercise.track_id,
        "track_title": exercise.track.title,
        "title": exercise.title,
        "problem_statement": exercise.problem_statement,
        "starter_code": exercise.starter_code,
        "language": exercise.language,
        "difficulty": exercise.difficulty,
        "estimated_minutes": exercise.estimated_minutes,
        "skill": exercise.skill,
        "tasks": exercise.tasks,
        "test_cases": exercise.test_cases,
    }


@app.get("/api/exercises")
def list_exercises(track: str | None = None, db: Session = Depends(get_db)):
    query = select(Exercise).options(joinedload(Exercise.track)).order_by(Exercise.id)
    if track:
        query = query.join(Track).where(Track.slug == track)
    return [serialize_exercise(exercise) for exercise in db.scalars(query).unique().all()]


@app.get("/api/exercises/{exercise_id}")
def exercise_details(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.scalar(select(Exercise).options(joinedload(Exercise.track)).where(Exercise.id == exercise_id))
    if exercise is None:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    return serialize_exercise(exercise)


@app.post("/api/submissions")
def submit_code(payload: SubmissionRequest, request: Request, db: Session = Depends(get_db)):
    user_id = require_user_id(request)
    exercise = db.get(Exercise, payload.exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    result = evaluate_submission(exercise, payload.code, payload.action)
    submission_status = (
        result["status"] if payload.action == "submit" else f"run_{result['status']}"
    )
    submission = Submission(
        user_id=user_id,
        exercise_id=exercise.id,
        code=payload.code,
        status=submission_status,
        score=result["score"],
        output=result,
    )
    db.add(submission)
    db.commit()
    result["submission_id"] = submission.id
    return result


@app.get("/api/submissions/mine")
def my_submissions(request: Request, db: Session = Depends(get_db)):
    user_id = require_user_id(request)
    entries = db.scalars(
        select(Submission)
        .options(joinedload(Submission.exercise))
        .where(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .limit(50)
    ).unique().all()
    return [{
        "id": entry.id,
        "exercise_id": entry.exercise_id,
        "exercise_title": entry.exercise.title,
        "status": entry.status,
        "score": entry.score,
        "created_at": entry.created_at,
    } for entry in entries]


@app.get("/api/progress/me")
def my_progress(request: Request, db: Session = Depends(get_db)):
    user_id = require_user_id(request)
    exercises = db.scalars(select(Exercise).options(joinedload(Exercise.track))).unique().all()
    best_scores = dict(db.execute(
        select(Submission.exercise_id, func.max(Submission.score))
        .where(Submission.user_id == user_id)
        .group_by(Submission.exercise_id)
    ).all())
    completed_ids = db.scalars(
        select(Submission.exercise_id)
        .where(Submission.user_id == user_id, Submission.status == "passed")
        .distinct()
    ).all()
    skill_totals = {}
    for exercise in exercises:
        if exercise.id in best_scores:
            skill_totals.setdefault(exercise.skill, []).append(best_scores[exercise.id])
    skills = [{
        "name": name,
        "score": round(sum(scores) / len(scores)) if scores else 0,
    } for name, scores in skill_totals.items()]
    submissions = db.scalars(
        select(Submission)
        .options(joinedload(Submission.exercise))
        .where(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .limit(5)
    ).unique().all()
    recent = [{
        "id": submission.id,
        "exercise_id": submission.exercise_id,
        "exercise_title": submission.exercise.title,
        "status": submission.status,
        "score": submission.score,
        "created_at": submission.created_at,
    } for submission in submissions]
    total_submissions = db.scalar(
        select(func.count(Submission.id)).where(Submission.user_id == user_id)
    ) or 0
    return {
        "completed_count": len(completed_ids),
        "completed_exercise_ids": completed_ids,
        "total_exercises": len(exercises),
        "completion_percent": round(len(completed_ids) / len(exercises) * 100) if exercises else 0,
        "total_submissions": total_submissions,
        "skills": skills,
        "recommended_exercise_id": next((exercise.id for exercise in exercises if exercise.id not in completed_ids), None),
        "recent_submissions": recent,
    }


@app.post("/api/assistant/hint")
def get_hint(payload: HintRequest, request: Request, db: Session = Depends(get_db)):
    require_user_id(request)
    exercise = db.get(Exercise, payload.exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    keywords = {
        "pagination": "Start by translating the page number into an offset, then slice the input and return the total before slicing.",
        "validation": "Check required fields before using them. Normalize whitespace, then validate the email shape and report invalid data clearly.",
        "sql_aggregation": "Use COUNT with GROUP BY so the database computes one result per customer, and filter completed orders before grouping.",
        "deduplication": "Keep a set of event IDs you have already seen, and append only the first occurrence to an ordered result list.",
        "immutable_state": "Create a new array when updating a line, then derive the total from the current items instead of caching stale state.",
    }
    return {"source": "built_in", "hint": keywords.get(exercise.evaluation_rule, "Trace one small input by hand and check the boundary cases before changing your implementation.")}
