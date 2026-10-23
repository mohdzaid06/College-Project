"""Flask JSON API for the placement preparation project."""

import json
import os
import re
from functools import wraps

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from database import connect_db, init_db, now_iso

FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://127.0.0.1:5173")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-key-change-me"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    CORS(app, origins=[FRONTEND_ORIGIN], supports_credentials=True)
    init_db()

    def error(message, status):
        return jsonify({"success": False, "error": message}), status

    def current_user():
        user_id = session.get("user_id")
        if not user_id:
            return None
        db = connect_db()
        user = db.execute("SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
        db.close()
        if user is None:
            session.clear()
            return None
        return dict(user)

    def login_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if current_user() is None:
                return error("Please log in to continue.", 401)
            return fn(*args, **kwargs)
        return wrapped

    def admin_required(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                return error("Please log in to continue.", 401)
            if user["role"] != "admin":
                return error("Administrator access is required.", 403)
            return fn(*args, **kwargs)
        return wrapped

    def as_job(row):
        item = dict(row)
        item["skills"] = [value.strip() for value in item["skills"].split(",") if value.strip()]
        item["is_sample"] = bool(item["is_sample"])
        return item

    def valid_job(data):
        fields = ["title", "company", "location", "job_type", "description"]
        if not isinstance(data, dict) or any(not isinstance(data.get(k), str) or not data[k].strip() for k in fields):
            return None
        skills = data.get("skills", [])
        if isinstance(skills, list):
            skills = ", ".join(str(x).strip() for x in skills if str(x).strip())
        if not isinstance(skills, str):
            return None
        instructions = data.get("instructions", "")
        if not isinstance(instructions, str):
            return None
        return {"title": data["title"].strip()[:120], "company": data["company"].strip()[:120], "location": data["location"].strip()[:120], "job_type": data["job_type"].strip()[:40], "description": data["description"].strip()[:3000], "skills": skills[:500], "instructions": instructions.strip()[:2000]}

    @app.get("/api/health")
    def health():
        return jsonify({"success": True, "data": {"status": "healthy"}})

    @app.get("/api/jobs")
    def list_jobs():
        search = request.args.get("search", "").strip()[:100]
        job_type = request.args.get("type", "").strip()[:40]
        location = request.args.get("location", "").strip()[:100]
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        if search:
            query += " AND (title LIKE ? OR company LIKE ?)"
            params.extend(["%" + search + "%", "%" + search + "%"])
        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)
        if location:
            query += " AND location LIKE ?"
            params.append("%" + location + "%")
        query += " ORDER BY id DESC"
        db = connect_db()
        rows = db.execute(query, params).fetchall()
        db.close()
        return jsonify({"success": True, "data": [as_job(row) for row in rows]})

    @app.get("/api/jobs/<int:job_id>")
    def get_job(job_id):
        db = connect_db()
        row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        db.close()
        if row is None:
            return error("Job listing not found.", 404)
        return jsonify({"success": True, "data": as_job(row)})

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        name, email, password = data.get("name"), data.get("email"), data.get("password")
        if not all(isinstance(v, str) for v in (name, email, password)):
            return error("Name, email, and password are required.", 400)
        name, email = name.strip(), email.strip().lower()
        if len(name) < 2 or len(name) > 80:
            return error("Name must be between 2 and 80 characters.", 400)
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return error("Enter a valid email address.", 400)
        if len(password) < 8 or len(password) > 128:
            return error("Password must be between 8 and 128 characters.", 400)
        db = connect_db()
        try:
            cursor = db.execute("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, 'student', ?)", (name, email, generate_password_hash(password, method="pbkdf2:sha256:600000"), now_iso()))
            db.commit()
            session.clear()
            session["user_id"] = cursor.lastrowid
            return jsonify({"success": True, "data": {"id": cursor.lastrowid, "name": name, "email": email, "role": "student"}}), 201
        except Exception as exc:
            db.rollback()
            if "UNIQUE" in str(exc):
                return error("An account with this email already exists.", 409)
            app.logger.exception("Registration failed")
            return error("Could not create the account.", 500)
        finally:
            db.close()

    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        email, password = data.get("email"), data.get("password")
        if not isinstance(email, str) or not isinstance(password, str):
            return error("Email and password are required.", 400)
        db = connect_db()
        row = db.execute("SELECT id, name, email, role, password_hash FROM users WHERE email = ? COLLATE NOCASE", (email.strip(),)).fetchone()
        db.close()
        if row is None or not check_password_hash(row["password_hash"], password):
            return error("Email or password is incorrect.", 401)
        session.clear()
        session["user_id"] = row["id"]
        return jsonify({"success": True, "data": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}})

    @app.post("/api/auth/logout")
    def logout():
        session.clear()
        return jsonify({"success": True, "data": {"message": "Logged out."}})

    @app.get("/api/auth/me")
    def me():
        user = current_user()
        if user is None:
            return error("Not logged in.", 401)
        return jsonify({"success": True, "data": user})

    @app.get("/api/questions")
    def list_questions():
        category = request.args.get("category", "").strip()[:40]
        db = connect_db()
        if category:
            rows = db.execute("SELECT id, category, prompt, options FROM questions WHERE category = ? ORDER BY id", (category,)).fetchall()
        else:
            rows = db.execute("SELECT id, category, prompt, options FROM questions ORDER BY id").fetchall()
        db.close()
        result = [dict(row) for row in rows]
        for item in result:
            item["options"] = json.loads(item["options"])
        return jsonify({"success": True, "data": result})

    @app.post("/api/quizzes/submit")
    def submit_quiz():
        data = request.get_json(silent=True) or {}
        answers = data.get("answers")
        category = data.get("category", "Mixed")
        if not isinstance(answers, dict) or not answers or len(answers) > 50 or not isinstance(category, str):
            return error("Submit answers for at least one question.", 400)
        try:
            normalized = {int(key): int(value) for key, value in answers.items()}
        except (ValueError, TypeError):
            return error("Answers must use question IDs and option numbers.", 400)
        db = connect_db()
        ids = list(normalized)
        placeholders = ",".join("?" for _ in ids)
        rows = db.execute("SELECT id, category, correct_answer, explanation FROM questions WHERE id IN (" + placeholders + ")", ids).fetchall()
        question_map = {row["id"]: row for row in rows}
        if len(question_map) != len(ids) or any(value < 0 or value > 3 for value in normalized.values()):
            db.close()
            return error("One or more submitted answers are invalid.", 400)
        score = sum(1 for qid, answer in normalized.items() if question_map[qid]["correct_answer"] == answer)
        total = len(normalized)
        feedback = [{"question_id": qid, "correct": question_map[qid]["correct_answer"] == answer, "correct_answer": question_map[qid]["correct_answer"], "explanation": question_map[qid]["explanation"]} for qid, answer in normalized.items()]
        user = current_user()
        attempt_id = None
        if user is not None:
            cursor = db.execute("INSERT INTO quiz_attempts (user_id, category, score, total, answers_json, created_at) VALUES (?, ?, ?, ?, ?, ?)", (user["id"], category[:40], score, total, json.dumps(normalized), now_iso()))
            db.commit()
            attempt_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "data": {"id": attempt_id, "category": category, "score": score, "total": total, "saved": user is not None, "feedback": feedback}}), 201

    @app.get("/api/results")
    @login_required
    def results():
        db = connect_db()
        rows = db.execute("SELECT id, category, score, total, created_at FROM quiz_attempts WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()
        db.close()
        return jsonify({"success": True, "data": [dict(row) for row in rows]})

    @app.get("/api/applications")
    @login_required
    def applications():
        db = connect_db()
        rows = db.execute("SELECT a.id, a.job_id, a.status, a.notes, a.created_at, a.updated_at, j.title, j.company, j.location, j.job_type FROM applications a JOIN jobs j ON j.id = a.job_id WHERE a.user_id = ? ORDER BY a.updated_at DESC", (session["user_id"],)).fetchall()
        db.close()
        return jsonify({"success": True, "data": [dict(row) for row in rows]})

    @app.post("/api/applications")
    @login_required
    def add_application():
        data = request.get_json(silent=True) or {}
        try:
            job_id = int(data.get("job_id"))
        except (ValueError, TypeError):
            return error("A valid job_id is required.", 400)
        status = data.get("status", "Saved")
        if status not in ("Saved", "Applied", "Interview", "Offered", "Rejected"):
            return error("Choose a valid application status.", 400)
        db = connect_db()
        if db.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone() is None:
            db.close()
            return error("Job listing not found.", 404)
        try:
            stamp = now_iso()
            cursor = db.execute("INSERT INTO applications (user_id, job_id, status, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], job_id, status, "", stamp, stamp))
            db.commit()
            result = cursor.lastrowid
        except Exception as exc:
            db.rollback()
            db.close()
            if "UNIQUE" in str(exc):
                return error("This job is already in your tracker.", 409)
            app.logger.exception("Could not save application")
            return error("Could not save this application.", 500)
        db.close()
        return jsonify({"success": True, "data": {"id": result, "job_id": job_id, "status": status}}), 201

    @app.patch("/api/applications/<int:application_id>")
    @login_required
    def update_application(application_id):
        data = request.get_json(silent=True) or {}
        status = data.get("status")
        if status not in ("Saved", "Applied", "Interview", "Offered", "Rejected"):
            return error("Choose a valid application status.", 400)
        db = connect_db()
        cursor = db.execute("UPDATE applications SET status = ?, updated_at = ? WHERE id = ? AND user_id = ?", (status, now_iso(), application_id, session["user_id"]))
        db.commit()
        db.close()
        if cursor.rowcount == 0:
            return error("Application not found.", 404)
        return jsonify({"success": True, "data": {"id": application_id, "status": status}})

    @app.post("/api/admin/jobs")
    @admin_required
    def create_job():
        job = valid_job(request.get_json(silent=True))
        if not job:
            return error("Provide title, company, location, job_type, and description as text.", 400)
        db = connect_db()
        cursor = db.execute("INSERT INTO jobs (title, company, location, job_type, description, skills, instructions, is_sample, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)", tuple(job[k] for k in ("title", "company", "location", "job_type", "description", "skills", "instructions")) + (now_iso(),))
        db.commit()
        job_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "data": {"id": job_id, **job, "skills": [s.strip() for s in job["skills"].split(",") if s.strip()], "is_sample": False}}), 201

    @app.get("/api/admin/jobs")
    @admin_required
    def admin_jobs():
        db = connect_db()
        rows = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
        db.close()
        return jsonify({"success": True, "data": [as_job(row) for row in rows]})

    @app.patch("/api/admin/jobs/<int:job_id>")
    @admin_required
    def edit_job(job_id):
        job = valid_job(request.get_json(silent=True))
        if not job:
            return error("Provide title, company, location, job_type, and description as text.", 400)
        db = connect_db()
        cursor = db.execute("UPDATE jobs SET title=?, company=?, location=?, job_type=?, description=?, skills=?, instructions=? WHERE id=?", tuple(job[k] for k in ("title", "company", "location", "job_type", "description", "skills", "instructions")) + (job_id,))
        db.commit()
        db.close()
        if cursor.rowcount == 0:
            return error("Job listing not found.", 404)
        return jsonify({"success": True, "data": {"id": job_id, **job}})

    @app.delete("/api/admin/jobs/<int:job_id>")
    @admin_required
    def delete_job(job_id):
        db = connect_db()
        cursor = db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        db.commit()
        db.close()
        if cursor.rowcount == 0:
            return error("Job listing not found.", 404)
        return jsonify({"success": True, "data": {"deleted": True}})

    @app.post("/api/admin/questions")
    @admin_required
    def create_question():
        data = request.get_json(silent=True) or {}
        category, prompt, options = data.get("category"), data.get("prompt"), data.get("options")
        correct, explanation = data.get("correct_answer"), data.get("explanation", "")
        if not isinstance(category, str) or not category.strip() or not isinstance(prompt, str) or not prompt.strip() or not isinstance(options, list) or len(options) != 4 or not all(isinstance(x, str) and x.strip() for x in options) or not isinstance(correct, int) or correct not in range(4) or not isinstance(explanation, str):
            return error("Provide category, prompt, four options, correct_answer (0–3), and explanation.", 400)
        db = connect_db()
        cursor = db.execute("INSERT INTO questions (category, prompt, options, correct_answer, explanation, is_sample, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)", (category.strip()[:40], prompt.strip()[:1000], json.dumps(options), correct, explanation.strip()[:1000], now_iso()))
        db.commit()
        question_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "data": {"id": question_id}}), 201

    @app.get("/api/admin/questions")
    @admin_required
    def admin_questions():
        db = connect_db()
        rows = db.execute("SELECT * FROM questions ORDER BY id DESC").fetchall()
        db.close()
        result = [dict(row) for row in rows]
        for item in result:
            item["options"] = json.loads(item["options"])
        return jsonify({"success": True, "data": result})

    @app.patch("/api/admin/questions/<int:question_id>")
    @admin_required
    def edit_question(question_id):
        data = request.get_json(silent=True) or {}
        category, prompt, options = data.get("category"), data.get("prompt"), data.get("options")
        correct, explanation = data.get("correct_answer"), data.get("explanation", "")
        if not isinstance(category, str) or not category.strip() or not isinstance(prompt, str) or not prompt.strip() or not isinstance(options, list) or len(options) != 4 or not all(isinstance(x, str) and x.strip() for x in options) or not isinstance(correct, int) or correct not in range(4) or not isinstance(explanation, str):
            return error("Provide category, prompt, four options, correct_answer (0–3), and explanation.", 400)
        db = connect_db()
        cursor = db.execute("UPDATE questions SET category=?, prompt=?, options=?, correct_answer=?, explanation=? WHERE id=?", (category.strip()[:40], prompt.strip()[:1000], json.dumps(options), correct, explanation.strip()[:1000], question_id))
        db.commit()
        db.close()
        if cursor.rowcount == 0:
            return error("Question not found.", 404)
        return jsonify({"success": True, "data": {"id": question_id}})

    @app.delete("/api/admin/questions/<int:question_id>")
    @admin_required
    def delete_question(question_id):
        db = connect_db()
        cursor = db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        db.commit()
        db.close()
        if cursor.rowcount == 0:
            return error("Question not found.", 404)
        return jsonify({"success": True, "data": {"deleted": True}})

    @app.errorhandler(404)
    def not_found(_exc):
        return error("API endpoint not found.", 404)

    @app.errorhandler(413)
    def too_large(_exc):
        return error("Request body is too large.", 413)

    @app.errorhandler(500)
    def server_error(_exc):
        return error("An unexpected server error occurred.", 500)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
