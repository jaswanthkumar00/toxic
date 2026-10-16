
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()

app = FastAPI(
    title="SkillForge AI",
    description="A practical coding skills platform for fresh graduates",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this when deploying
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI is optional; the core application works without an API key.
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Sample practical coding challenges
CHALLENGES = [
    {
        "id": 1,
        "title": "Fix a Bug",
        "skill": "debugging",
        "difficulty": "beginner",
        "description": (
            "Fix the function so that it returns the sum "
            "of two numbers."
        ),
        "starter_code": (
            "def add_numbers(a, b):\n"
            "    return a - b\n"
        ),
        "expected_behavior": "Return a + b",
    },
    {
        "id": 2,
        "title": "Validate User Input",
        "skill": "problem_solving",
        "difficulty": "beginner",
        "description": (
            "Write a function that returns True when "
            "the input is a non-empty string."
        ),
        "starter_code": "def is_valid_name(name):\n    pass\n",
        "expected_behavior": "Accept non-empty strings",
    },
    {
        "id": 3,
        "title": "Remove Duplicates",
        "skill": "data_structures",
        "difficulty": "intermediate",
        "description": (
            "Return a list with duplicates removed, "
            "preserving the original order."
        ),
        "starter_code": "def remove_duplicates(items):\n    pass\n",
        "expected_behavior": "Preserve order and unique values",
    },
]

# Simple in-memory progress store for the MVP.
# Replace with a database for persistent, multi-user progress.
PROGRESS = {}


class Submission(BaseModel):
    learner_id: str = Field(min_length=1, max_length=100)
    challenge_id: int
    code: str = Field(min_length=1, max_length=10000)


class HintRequest(BaseModel):
    challenge_id: int
    code: str = Field(default="", max_length=10000)
    error_message: str = Field(default="", max_length=3000)


class ProgressUpdate(BaseModel):
    learner_id: str = Field(min_length=1, max_length=100)
    challenge_id: int
    completed: bool


def get_challenge(challenge_id: int):
    for challenge in CHALLENGES:
        if challenge["id"] == challenge_id:
            return challenge
    raise HTTPException(status_code=404, detail="Challenge not found")


@app.get("/")
def home():
    return {
        "message": "Welcome to SkillForge AI!",
        "purpose": "Build practical software development skills",
        "features": [
            "Real-world coding challenges",
            "Automated code evaluation",
            "AI-powered hints",
            "Skill progress tracking",
        ],
    }


@app.get("/challenges")
def list_challenges():
    """Return available coding challenges."""
    return CHALLENGES


@app.get("/challenges/{challenge_id}")
def challenge_details(challenge_id: int):
    """Return details for one challenge."""
    return get_challenge(challenge_id)


@app.post("/hint")
def get_hint(request: HintRequest):
    """Give a graduated hint using OpenAI when configured."""
    challenge = get_challenge(request.challenge_id)

    if client is None:
        return {
            "source": "built_in",
            "hint": (
                "Read the task carefully, trace your code "
                "with a small example, and check edge cases. "
                "Try to solve it before looking at a full answer."
            ),
        }

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are a supportive programming mentor for "
                "fresh graduates. Give one useful hint at a time. "
                "Do not reveal the complete solution immediately. "
                "Explain the reasoning in beginner-friendly language."
            ),
            input=(
                f"Challenge: {challenge['description']}\n"
                f"Learner code:\n{request.code}\n"
                f"Error message: {request.error_message}\n"
                "Provide the next hint, not the full solution."
            ),
        )

        return {
            "source": "openai",
            "hint": response.output_text,
        }

    except Exception:
        return {
            "source": "built_in",
            "hint": (
                "The AI mentor is temporarily unavailable. "
                "Trace your code manually and test a simple input."
            ),
        }


@app.post("/submit")
def submit_code(submission: Submission):
    """
    Evaluate supported beginner exercises using predefined tests.

    This MVP deliberately does not execute arbitrary submitted code.
    """
    challenge = get_challenge(submission.challenge_id)
    code = submission.code.strip()

    # Basic starter challenge: verify the function's behavior
    # using a small, predefined set of accepted implementations.
    if challenge["id"] == 1:
        accepted = (
            "return a + b" in code
            and "def add_numbers" in code
        )
        tests = [
            {"input": [2, 3], "expected": 5},
            {"input": [-1, 1], "expected": 0},
        ]
        feedback = (
            "Your implementation appears to use addition."
            if accepted
            else "Check whether your function adds the two inputs."
        )

    elif challenge["id"] == 2:
        accepted = (
            "def is_valid_name" in code
            and "return" in code
            and "strip" in code
        )
        tests = [
            {"input": ["Alex"], "expected": True},
            {"input": [""], "expected": False},
        ]
        feedback = (
            "Your code includes a basic validation approach."
            if accepted
            else "Consider empty strings and strings containing spaces."
        )

    else:
        accepted = (
            "def remove_duplicates" in code
            and "return" in code
            and "set(" not in code
        )
        tests = [
            {"input": [[1, 2, 1]], "expected": [1, 2]},
        ]
        feedback = (
            "Your code has a return statement. Verify that order is preserved."
            if accepted
            else "Think about how to track seen items without losing order."
        )

    # This is a preliminary heuristic, not actual test execution.
    return {
        "challenge_id": challenge["id"],
        "skill": challenge["skill"],
        "preliminary_pass": accepted,
        "evaluation_type": "heuristic",
        "sample_tests": tests,
        "feedback": feedback,
        "note": (
            "This MVP checks code patterns, not actual runtime behavior. "
            "Use isolated execution and real unit tests for reliable grading."
        ),
    }


@app.post("/progress")
def update_progress(update: ProgressUpdate):
    """Record a learner's challenge completion."""
    challenge = get_challenge(update.challenge_id)

    learner = PROGRESS.setdefault(
        update.learner_id,
        {"completed": [], "skills": {}},
    )

    if update.completed and update.challenge_id not in learner["completed"]:
        learner["completed"].append(update.challenge_id)
        skill = challenge["skill"]
        learner["skills"][skill] = learner["skills"].get(skill, 0) + 1

    return {
        "learner_id": update.learner_id,
        "completed_challenges": learner["completed"],
        "skill_activity": learner["skills"],
    }


@app.get("/progress/{learner_id}")
def get_progress(learner_id: str):
    """Retrieve progress for a learner."""
    learner = PROGRESS.get(
        learner_id,
        {"completed": [], "skills": {}},
    )

    return {
        "learner_id": learner_id,
        "total_challenges": len(CHALLENGES),
        "completed_count": len(learner["completed"]),
        "skills_practiced": learner["skills"],
        "completed_challenges": learner["completed"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Initialize the Gemini client using the key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Send a test prompt
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello! Confirm that the API is connected successfully.",
)

print(response.text)