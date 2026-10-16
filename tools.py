
"""
SkillForge AI - Practical Coding Utilities

Provides:
- Challenge validation
- Python syntax checking
- Safe, deterministic skill scoring
- Test result summaries
- Challenge definition validation

Important:
This module does not execute learner-submitted code.
Use a properly isolated sandbox for execution.
"""

import ast
from typing import Any, Dict, List, Optional


# --------------------------------------------------
# 1. Validate challenge definitions
# --------------------------------------------------

REQUIRED_CHALLENGE_FIELDS = {
    "id",
    "title",
    "skill",
    "difficulty",
    "description",
}


def validate_challenge(challenge: Dict[str, Any]) -> Dict[str, Any]:
    """Check that a challenge contains required fields."""

    missing = REQUIRED_CHALLENGE_FIELDS - set(challenge.keys())

    if missing:
        return {
            "valid": False,
            "errors": [
                f"Missing required field: {field}"
                for field in sorted(missing)
            ],
        }

    allowed_difficulties = {
        "beginner",
        "intermediate",
        "advanced",
    }

    errors = []

    if not isinstance(challenge["id"], int):
        errors.append("Challenge ID must be an integer.")

    for field in ("title", "skill", "description"):
        if not isinstance(challenge[field], str) or not challenge[field].strip():
            errors.append(f"{field} must be a non-empty string.")

    if challenge["difficulty"] not in allowed_difficulties:
        errors.append(
            "Difficulty must be beginner, intermediate, or advanced."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# --------------------------------------------------
# 2. Check Python syntax
# --------------------------------------------------

def check_python_syntax(code: str) -> Dict[str, Any]:
    """
    Parse Python code without executing it.

    This checks syntax only, not whether the program
    produces the correct output.
    """

    if not isinstance(code, str) or not code.strip():
        return {
            "valid": False,
            "error": "No Python code was provided.",
            "line": None,
        }

    try:
        ast.parse(code)

        return {
            "valid": True,
            "error": None,
            "line": None,
        }

    except SyntaxError as exc:
        return {
            "valid": False,
            "error": exc.msg,
            "line": exc.lineno,
        }


# --------------------------------------------------
# 3. Check required code patterns
# --------------------------------------------------

def check_required_patterns(
    code: str,
    required_patterns: List[str],
) -> Dict[str, Any]:
    """
    Check whether specified text patterns appear in code.

    This is a basic helper, not a correctness evaluator.
    """

    if not isinstance(code, str):
        return {
            "passed": False,
            "found": [],
            "missing": list(required_patterns),
        }

    found = [
        pattern
        for pattern in required_patterns
        if pattern in code
    ]

    missing = [
        pattern
        for pattern in required_patterns
        if pattern not in code
    ]

    return {
        "passed": len(missing) == 0,
        "found": found,
        "missing": missing,
    }


# --------------------------------------------------
# 4. Summarize actual test results
# --------------------------------------------------

def summarize_test_results(
    test_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Summarize results produced by a trusted test runner.

    Each result should look like:
    {"name": "test_add", "passed": True}

    Only pass verified results from your test runner.
    """

    passed = 0
    failed = 0
    details = []

    for result in test_results:
        name = str(result.get("name", "unnamed test"))
        status = result.get("passed")

        if not isinstance(status, bool):
            details.append({
                "name": name,
                "status": "invalid_result",
            })
            continue

        if status:
            passed += 1
            details.append({
                "name": name,
                "status": "passed",
            })
        else:
            failed += 1
            details.append({
                "name": name,
                "status": "failed",
            })

    total = passed + failed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "score_percentage": round(
            (passed / total) * 100, 2
        ) if total else 0,
        "results": details,
    }


# --------------------------------------------------
# 5. Calculate a practical skill score
# --------------------------------------------------

def calculate_skill_score(
    correctness: Optional[int] = None,
    debugging: Optional[int] = None,
    testing: Optional[int] = None,
    readability: Optional[int] = None,
    problem_solving: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate a weighted score using ratings from 0 to 4.

    Unassessed dimensions are excluded from the calculation.
    This is a progress indicator, not a job-readiness verdict.
    """

    dimensions = {
        "correctness": (correctness, 0.40),
        "debugging": (debugging, 0.20),
        "testing": (testing, 0.15),
        "readability": (readability, 0.10),
        "problem_solving": (problem_solving, 0.15),
    }

    weighted_total = 0.0
    available_weight = 0.0
    assessed = {}

    for name, (score, weight) in dimensions.items():
        if score is None:
            continue

        if isinstance(score, bool) or not isinstance(score, int):
            raise ValueError(
                f"{name} must be an integer from 0 to 4."
            )

        if score < 0 or score > 4:
            raise ValueError(
                f"{name} must be between 0 and 4."
            )

        assessed[name] = score
        weighted_total += (score / 4) * weight
        available_weight += weight

    if available_weight == 0:
        return {
            "score_percentage": None,
            "assessed_dimensions": 0,
            "feedback": "Complete an assessment to measure progress.",
        }

    percentage = round(
        (weighted_total / available_weight) * 100, 2
    )

    return {
        "score_percentage": percentage,
        "assessed_dimensions": len(assessed),
        "dimension_scores": assessed,
        "feedback": get_score_feedback(percentage),
    }


def get_score_feedback(score: float) -> str:
    """Return supportive feedback for a progress score."""

    if score >= 85:
        return "Strong performance. Try a more challenging task."

    if score >= 65:
        return "Good progress. Practice edge cases and testing."

    if score >= 40:
        return "Keep practicing. Work through smaller tasks first."

    return (
        "Focus on understanding the fundamentals and use "
        "step-by-step hints to build confidence."
    )


# --------------------------------------------------
# 6. Generate a learning recommendation
# --------------------------------------------------

def recommend_practice(
    skill_scores: Dict[str, int],
) -> Dict[str, str]:
    """
    Recommend practice based on recorded skill ratings.

    Lower ratings indicate areas that may need more practice.
    """

    recommendations = {
        "debugging": "Practice tracing errors and fixing small bugs.",
        "testing": "Write unit tests for normal and edge cases.",
        "correctness": "Practice translating requirements into solutions.",
        "readability": "Improve naming, formatting, and code structure.",
        "problem_solving": "Break problems into smaller steps.",
        "api_development": "Practice HTTP responses and input validation.",
        "git": "Practice branches, commits, and code reviews.",
    }

    if not skill_scores:
        return {
            "priority_skill": "problem_solving",
            "recommendation": (
                "Start with a beginner coding challenge "
                "to establish a baseline."
            ),
        }

    for skill, score in skill_scores.items():
        if isinstance(score, bool) or not isinstance(score, int):
            raise ValueError(
                f"Score for {skill} must be an integer."
            )

        if score < 0 or score > 4:
            raise ValueError(
                f"Score for {skill} must be between 0 and 4."
            )

    priority_skill = min(skill_scores, key=skill_scores.get)

    return {
        "priority_skill": priority_skill,
        "recommendation": recommendations.get(
            priority_skill,
            "Complete another practical challenge in this skill.",
        ),
    }


# --------------------------------------------------
# 7. Quick local test
# --------------------------------------------------

if __name__ == "__main__":
    print("SkillForge AI tools are ready!")

    example_code = """
def add_numbers(a, b):
    return a + b
"""

    print("\nSyntax check:")
    print(check_python_syntax(example_code))

    print("\nTest summary:")
    print(
        summarize_test_results([
            {"name": "test_positive_numbers", "passed": True},
            {"name": "test_negative_numbers", "passed": True},
            {"name": "test_edge_case", "passed": False},
        ])
    )

    print("\nSkill score:")
    print(
        calculate_skill_score(
            correctness=4,
            debugging=3,
            testing=2,
            readability=3,
            problem_solving=3,
        )
    )

    print("\nPractice recommendation:")
    print(
        recommend_practice({
            "debugging": 3,
            "testing": 1,
            "readability": 2,
        })
    )
