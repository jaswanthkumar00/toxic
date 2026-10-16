import os
import unittest
from uuid import uuid4

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./.test-skillforge.db"
os.environ["SECRET_KEY"] = "test-secret-key-with-more-than-32-characters"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"
os.environ.pop("SEED_INSTRUCTOR_EMAIL", None)
os.environ.pop("SEED_INSTRUCTOR_PASSWORD", None)

from fastapi.testclient import TestClient

from backend.main import app


class SkillForgeApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_context = TestClient(app)
        cls.app_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.__exit__(None, None, None)

    def setUp(self):
        self.client = TestClient(app)

    def register(self):
        email = f"{uuid4().hex}@example.com"
        response = self.client.post("/api/auth/register", json={
            "name": "Test Learner",
            "email": email,
            "password": "a-secure-test-password",
        })
        self.assertEqual(response.status_code, 201, response.text)
        return email

    def test_catalog_is_seeded_and_contains_five_exercises(self):
        tracks = self.client.get("/api/tracks")
        exercises = self.client.get("/api/exercises")
        self.assertEqual(tracks.status_code, 200)
        self.assertGreaterEqual(len(tracks.json()), 3)
        self.assertEqual(len(exercises.json()), 5)
        self.assertTrue(all(len(exercise["tasks"]) == 3 for exercise in exercises.json()))

    def test_account_is_student_and_progress_requires_authentication(self):
        self.assertEqual(self.client.get("/api/progress/me").status_code, 401)
        self.register()
        account = self.client.get("/api/auth/me")
        self.assertEqual(account.status_code, 200)
        self.assertEqual(account.json()["role"], "student")
        progress = self.client.get("/api/progress/me")
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(progress.json()["completed_count"], 0)

    def test_registration_rejects_duplicate_email(self):
        email = self.register()
        duplicate = self.client.post("/api/auth/register", json={
            "name": "Another Learner",
            "email": email,
            "password": "a-secure-test-password",
        })
        self.assertEqual(duplicate.status_code, 409)

    def test_public_registration_cannot_claim_the_instructor_email(self):
        os.environ["SEED_INSTRUCTOR_EMAIL"] = "reserved@example.com"
        try:
            response = self.client.post("/api/auth/register", json={
                "name": "Attempted Instructor",
                "email": "reserved@example.com",
                "password": "a-secure-test-password",
            })
        finally:
            os.environ.pop("SEED_INSTRUCTOR_EMAIL", None)
        self.assertEqual(response.status_code, 409)

    def test_login_verifies_credentials_and_reissues_a_session(self):
        email = self.register()
        self.client.post("/api/auth/logout")
        invalid = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "incorrect-password",
        })
        self.assertEqual(invalid.status_code, 401)
        valid = self.client.post("/api/auth/login", json={
            "email": email,
            "password": "a-secure-test-password",
        })
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(valid.json()["email"], email)

    def test_static_assessment_persists_submission_and_progress(self):
        self.register()
        exercises = self.client.get("/api/exercises").json()
        exercise = next(item for item in exercises if item["slug"] == "repair-api-pagination")
        code = (
            "def paginate(items, page, page_size):\n"
            "    offset = (page - 1) * page_size\n"
            "    total = len(items)\n"
            "    return {'items': items[offset:offset + page_size], 'total': total}\n"
        )
        run = self.client.post("/api/submissions", json={
            "exercise_id": exercise["id"],
            "code": code,
            "action": "run",
        })
        self.assertEqual(run.status_code, 200, run.text)
        self.assertEqual(self.client.get("/api/progress/me").json()["completed_count"], 0)
        submission = self.client.post("/api/submissions", json={
            "exercise_id": exercise["id"],
            "code": code,
            "action": "submit",
        })
        self.assertEqual(submission.status_code, 200, submission.text)
        result = submission.json()
        self.assertEqual(result["evaluation_type"], "static_mock")
        self.assertEqual(result["score"], 100)
        progress = self.client.get("/api/progress/me").json()
        self.assertEqual(progress["completed_count"], 1)
        self.assertIn(exercise["id"], progress["completed_exercise_ids"])

    def test_hint_requires_a_valid_exercise_and_authenticated_user(self):
        self.register()
        response = self.client.post("/api/assistant/hint", json={
            "exercise_id": 99999,
            "code": "",
        })
        self.assertEqual(response.status_code, 404)

    def test_sign_out_clears_session(self):
        self.register()
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)


if __name__ == "__main__":
    unittest.main()
