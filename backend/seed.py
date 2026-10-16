from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Exercise, Track

TRACKS = [
    {
        "slug": "backend-engineering",
        "title": "Backend engineering",
        "description": "Build resilient APIs, validate inputs, and handle real-world data.",
        "level": "Intermediate",
        "icon": "server",
        "exercises": [
            {
                "slug": "repair-api-pagination",
                "title": "Repair API pagination",
                "problem_statement": "A production endpoint returns every record and leaks inconsistent paging metadata. Implement a bounded page size, offset-based slicing, and total-count metadata. Handle an empty result set.",
                "starter_code": "def paginate(items, page, page_size):\n    # Return items, total, page, and page_size.\n    pass\n",
                "difficulty": "Intermediate",
                "skill": "API design",
                "estimated_minutes": 25,
                "evaluation_rule": "pagination",
                "tasks": [
                    "Inspect the endpoint contract and identify the paging edge cases.",
                    "Calculate the offset and keep the requested page size bounded.",
                    "Return the sliced items with consistent total and page metadata.",
                ],
                "test_cases": [
                    {"name": "slices the requested page", "input": [[1, 2, 3, 4], 2, 2], "expected": {"items": [3, 4], "total": 4}},
                    {"name": "handles empty collections", "input": [[], 1, 10], "expected": {"items": [], "total": 0}},
                    {"name": "caps oversized pages", "input": [[1, 2, 3], 1, 100], "expected": {"items": [1, 2, 3], "total": 3}},
                ],
            },
            {
                "slug": "validate-rest-payload",
                "title": "Validate a REST payload",
                "problem_statement": "Harden a user-registration endpoint by validating a required email and display name. Reject malformed or missing values with a clear validation error; never trust client-side checks alone.",
                "starter_code": "def validate_registration(payload):\n    # Return normalized data or raise ValueError.\n    pass\n",
                "difficulty": "Beginner",
                "skill": "Input validation",
                "estimated_minutes": 20,
                "evaluation_rule": "validation",
                "tasks": [
                    "List the required fields and reject missing values.",
                    "Normalize user-entered whitespace before validating.",
                    "Return clear errors for malformed registrations.",
                ],
                "test_cases": [
                    {"name": "accepts a valid registration", "input": [{"name": "Riley", "email": "riley@example.com"}], "expected": "normalized registration"},
                    {"name": "rejects missing fields", "input": [{"name": "Riley"}], "expected": "validation error"},
                    {"name": "trims user-entered whitespace", "input": [{"name": " Riley ", "email": "riley@example.com"}], "expected": "Riley"},
                ],
            },
        ],
    },
    {
        "slug": "data-and-testing",
        "title": "Data & test engineering",
        "description": "Make queries, tests, and core data transformations dependable.",
        "level": "Beginner",
        "icon": "database",
        "exercises": [
            {
                "slug": "optimize-sql-report",
                "title": "Optimize a slow SQL report",
                "problem_statement": "A dashboard counts all completed orders by customer. Replace the per-customer query pattern with a single grouped query. Keep only completed orders and return customer_id with order_count.",
                "starter_code": "query = \"\"\"\nSELECT customer_id\nFROM orders\n\"\"\"\n",
                "language": "sql",
                "difficulty": "Intermediate",
                "skill": "SQL",
                "estimated_minutes": 20,
                "evaluation_rule": "sql_aggregation",
                "tasks": [
                    "Find the per-customer query pattern and its repeated work.",
                    "Aggregate order counts with one grouped query.",
                    "Filter completed orders and select the report columns.",
                ],
                "test_cases": [
                    {"name": "groups counts by customer", "input": "orders", "expected": "one grouped result"},
                    {"name": "filters completed orders", "input": "mixed order statuses", "expected": "completed only"},
                    {"name": "returns one aggregate query", "input": "multiple customers", "expected": "one grouped query"},
                ],
            },
            {
                "slug": "remove-duplicate-events",
                "title": "Deduplicate webhook events",
                "problem_statement": "Webhook delivery can retry the same event. Return the first occurrence of each event_id in its original order, ignoring duplicate deliveries without changing the payload.",
                "starter_code": "def unique_events(events):\n    # Preserve first-seen order.\n    pass\n",
                "difficulty": "Beginner",
                "skill": "Data structures",
                "estimated_minutes": 15,
                "evaluation_rule": "deduplication",
                "tasks": [
                    "Choose a way to remember event IDs already delivered.",
                    "Keep the first occurrence in the original event order.",
                    "Return the unique events without modifying their payloads.",
                ],
                "test_cases": [
                    {"name": "keeps first event occurrence", "input": [{"event_id": "a"}, {"event_id": "b"}, {"event_id": "a"}], "expected": ["a", "b"]},
                    {"name": "returns an empty list for empty input", "input": [], "expected": []},
                    {"name": "preserves order across repeated deliveries", "input": ["a", "b", "a", "c"], "expected": ["a", "b", "c"]},
                ],
            },
        ],
    },
    {
        "slug": "frontend-quality",
        "title": "Frontend quality",
        "description": "Debug interface state and prevent regressions with focused tests.",
        "level": "Intermediate",
        "icon": "layout",
        "exercises": [
            {
                "slug": "fix-stale-cart-state",
                "title": "Fix stale cart state",
                "problem_statement": "A cart total becomes stale after a quantity update because the UI mutates shared state and reuses a previous total. Implement an immutable update and derive the total from the current cart lines.",
                "starter_code": "function updateQuantity(items, id, quantity) {\n  // Return updated items without mutating the original.\n}\n\nfunction cartTotal(items) {\n  // Derive the current total from item prices and quantities.\n}\n",
                "language": "javascript",
                "difficulty": "Intermediate",
                "skill": "State management",
                "estimated_minutes": 30,
                "evaluation_rule": "immutable_state",
                "tasks": [
                    "Trace how a quantity change affects the rendered cart.",
                    "Update the selected line without mutating shared state.",
                    "Derive the displayed total from the current cart items.",
                ],
                "test_cases": [
                    {"name": "updates the selected item", "input": "two cart lines", "expected": "updated selected quantity"},
                    {"name": "leaves the original state untouched", "input": "frozen cart input", "expected": "original unchanged"},
                    {"name": "recomputes totals from current quantities", "input": "updated cart", "expected": "current total"},
                ],
            },
        ],
    },
]


def seed_database(db: Session) -> None:
    for track_data in TRACKS:
        track = db.scalar(select(Track).where(Track.slug == track_data["slug"]))
        if track is None:
            track = Track(**{key: value for key, value in track_data.items() if key != "exercises"})
            db.add(track)
            db.flush()
        for exercise_data in track_data["exercises"]:
            existing = db.scalar(select(Exercise).where(Exercise.slug == exercise_data["slug"]))
            if existing is None:
                db.add(Exercise(track_id=track.id, **exercise_data))
    db.commit()


if __name__ == "__main__":
    from backend.database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)
    print("SkillForge challenge catalog is up to date.")
