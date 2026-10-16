import ast
import time

from backend.models import Exercise


def evaluate_submission(exercise: Exercise, code: str, action: str) -> dict:
    """Return mock assessment results without executing untrusted learner code."""
    started = time.perf_counter()
    rule = exercise.evaluation_rule
    normalized = code.lower()
    syntax_error = None

    if exercise.language == "python":
        try:
            ast.parse(code)
        except SyntaxError as exc:
            syntax_error = f"Syntax error on line {exc.lineno}: {exc.msg}"

    checks = {
        "pagination": [
            ("calculates a page offset", "page" in normalized and ("offset" in normalized or "*" in normalized)),
            ("returns total-count metadata", "total" in normalized and "len(" in normalized),
            ("slices results safely", ":" in code),
        ],
        "validation": [
            ("checks required fields", "email" in normalized and "name" in normalized),
            ("rejects invalid input", "raise" in normalized or "false" in normalized or "none" in normalized),
            ("normalizes user input", "strip" in normalized),
        ],
        "sql_aggregation": [
            ("aggregates in the database", "group by" in normalized and "count(" in normalized),
            ("filters completed orders", "where" in normalized and "completed" in normalized),
            ("selects customer and count", "customer_id" in normalized and ("order_count" in normalized or " as " in normalized)),
        ],
        "deduplication": [
            ("tracks seen event identifiers", "event_id" in normalized and ("seen" in normalized or "set" in normalized)),
            ("preserves first-seen order", "append" in normalized or "result" in normalized),
            ("returns the filtered events", "return" in normalized),
        ],
        "immutable_state": [
            ("updates items immutably", "map(" in normalized or "..." in code or "spread" in normalized),
            ("matches the requested item", "id" in normalized and "quantity" in normalized),
            ("derives totals from current items", "reduce(" in normalized or "reduce" in normalized),
        ],
    }.get(rule, [("provides an implementation", len(code.strip()) > 20)])

    if syntax_error:
        checks = [(syntax_error, False)]
    results = [{"name": name, "passed": passed} for name, passed in checks]
    passed = sum(1 for result in results if result["passed"])
    score = round(passed / len(results) * 100) if results else 0
    success = passed == len(results)
    return {
        "status": "passed" if success else "needs_work",
        "score": score,
        "evaluation_type": "static_mock",
        "execution_time_ms": round((time.perf_counter() - started) * 1000, 2),
        "output": (
            "Mock assessment complete. No learner code was executed."
            if action == "run"
            else ("All rubric checks passed." if success else "Review the failed checks and try again.")
        ),
        "test_results": results,
        "passed_count": passed,
        "total_count": len(results),
        "hint": next((result["name"] for result in results if not result["passed"]), None),
        "code_quality": {
            "line_count": len(code.splitlines()),
            "has_tests": "test" in normalized,
            "score": max(0, min(100, score - (10 if len(code.splitlines()) > 80 else 0))),
        },
    }

