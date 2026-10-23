import os
import tempfile
import unittest

import database
from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".sqlite")
        os.close(handle)
        database.DATABASE_PATH = self.path
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            os.unlink(self.path)
        except FileNotFoundError:
            pass

    def register(self, email="student@example.test", name="Test Student"):
        return self.client.post("/api/auth/register", json={"name": name, "email": email, "password": "test-password-123"})

    def test_health_and_seeded_jobs(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.get("/api/jobs?search=Python")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Python" in job["title"] for job in response.json["data"]))

    def test_registration_hashes_password_and_rejects_duplicate(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        duplicate = self.register()
        self.assertEqual(duplicate.status_code, 409)
        db = database.connect_db()
        password_hash = db.execute("SELECT password_hash FROM users").fetchone()[0]
        db.close()
        self.assertNotEqual(password_hash, "test-password-123")

    def test_login_validation_and_quiz_scoring(self):
        self.register()
        self.client.post("/api/auth/logout")
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "student@example.test", "password": "wrong"}).status_code, 401)
        login = self.client.post("/api/auth/login", json={"email": "student@example.test", "password": "test-password-123"})
        self.assertEqual(login.status_code, 200)
        questions = self.client.get("/api/questions").json["data"]
        result = self.client.post("/api/quizzes/submit", json={"category": "Mixed", "answers": {str(questions[0]["id"]): 1}})
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json["data"]["score"], 1)
        self.assertEqual(len(self.client.get("/api/results").json["data"]), 1)

    def test_application_ownership(self):
        self.register()
        first_job = self.client.get("/api/jobs").json["data"][0]["id"]
        created = self.client.post("/api/applications", json={"job_id": first_job})
        self.assertEqual(created.status_code, 201)
        application_id = created.json["data"]["id"]
        self.client.post("/api/auth/logout")
        self.register("other@example.test", "Other Student")
        self.assertEqual(self.client.patch("/api/applications/" + str(application_id), json={"status": "Offered"}).status_code, 404)
        self.assertEqual(self.client.get("/api/applications").json["data"], [])

    def test_admin_routes_require_admin(self):
        self.register()
        payload = {"title": "New Role", "company": "Example", "location": "Remote", "job_type": "Internship", "description": "Description"}
        self.assertEqual(self.client.post("/api/admin/jobs", json=payload).status_code, 403)
        self.assertEqual(self.client.get("/api/jobs/99999").status_code, 404)

    def test_admin_can_manage_jobs_and_questions(self):
        self.register()
        db = database.connect_db()
        db.execute("UPDATE users SET role = 'admin' WHERE email = ?", ("student@example.test",))
        db.commit()
        db.close()
        payload = {"title": "New Role", "company": "Example", "location": "Remote", "job_type": "Internship", "description": "Description", "skills": ["Python"], "instructions": "Read the role details."}
        created_job = self.client.post("/api/admin/jobs", json=payload)
        self.assertEqual(created_job.status_code, 201)
        job_id = created_job.json["data"]["id"]
        self.assertEqual(self.client.patch("/api/admin/jobs/" + str(job_id), json={**payload, "title": "Updated Role"}).status_code, 200)
        self.assertEqual(self.client.delete("/api/admin/jobs/" + str(job_id)).status_code, 200)
        question = {"category": "Technical", "prompt": "Which is correct?", "options": ["A", "B", "C", "D"], "correct_answer": 1, "explanation": "Example"}
        created_question = self.client.post("/api/admin/questions", json=question)
        self.assertEqual(created_question.status_code, 201)
        question_id = created_question.json["data"]["id"]
        self.assertEqual(self.client.patch("/api/admin/questions/" + str(question_id), json={**question, "prompt": "Updated?"}).status_code, 200)
        self.assertEqual(self.client.delete("/api/admin/questions/" + str(question_id)).status_code, 200)

    def test_seed_data_is_not_duplicated(self):
        database.init_db()
        database.init_db()
        db = database.connect_db()
        jobs = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        questions = db.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        db.close()
        self.assertEqual(jobs, 3)
        self.assertEqual(questions, 4)

    def test_guest_quiz_scores_without_saving_and_cors_is_narrow(self):
        question = self.client.get("/api/questions").json["data"][0]
        result = self.client.post("/api/quizzes/submit", json={"answers": {str(question["id"]): 1}})
        self.assertEqual(result.status_code, 201)
        self.assertFalse(result.json["data"]["saved"])
        self.assertEqual(self.client.get("/api/results").status_code, 401)
        allowed = self.client.options("/api/auth/login", headers={"Origin": "http://127.0.0.1:5173", "Access-Control-Request-Method": "POST"})
        blocked = self.client.options("/api/auth/login", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "POST"})
        self.assertEqual(allowed.headers.get("Access-Control-Allow-Origin"), "http://127.0.0.1:5173")
        self.assertIsNone(blocked.headers.get("Access-Control-Allow-Origin"))


if __name__ == "__main__":
    unittest.main()
