"""SQLite setup and sample data for Student Placement Preparation System."""

import os
import sqlite3
from datetime import datetime, timezone


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("VERCEL"):
    DATABASE_PATH = "/tmp/placement.db"
else:
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH",
        os.path.join(BASE_DIR, "placement.db")
    )




def connect_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection



def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db():
    connection = connect_db()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(name) BETWEEN 2 AND 80),
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student' CHECK(role IN ('student', 'admin')),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            description TEXT NOT NULL,
            skills TEXT NOT NULL DEFAULT '',
            instructions TEXT NOT NULL DEFAULT '',
            is_sample INTEGER NOT NULL DEFAULT 1 CHECK(is_sample IN (0, 1)),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            prompt TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer INTEGER NOT NULL CHECK(correct_answer BETWEEN 0 AND 3),
            explanation TEXT NOT NULL DEFAULT '',
            is_sample INTEGER NOT NULL DEFAULT 1 CHECK(is_sample IN (0, 1)),
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            answers_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            status TEXT NOT NULL DEFAULT 'Saved' CHECK(status IN ('Saved', 'Applied', 'Interview', 'Offered', 'Rejected')),
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, job_id)
        );
        """
    )
    if connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0:
        jobs = [
            ("Frontend Developer Intern", "Sample Company A", "Bengaluru / Remote", "Internship", "Practice building responsive interfaces with guidance from a product team. This is fictional sample data for demonstration.", "HTML, CSS, JavaScript, React", "Use the company's official careers page to explore similar opportunities.", 1, now_iso()),
            ("Python Developer Trainee", "Sample Company B", "Pune", "Full-time", "A fictional entry-level training role used to demonstrate the jobs module. It is not a live vacancy.", "Python, Flask, SQL, Git", "Sample listing only. No real application link is provided.", 1, now_iso()),
            ("Data Analyst Intern", "Sample Company C", "Remote", "Internship", "A fictional internship listing for practicing job search and application tracking.", "Excel, SQL, Python, Communication", "Sample listing only. Check verified employer sources for real openings.", 1, now_iso()),
        ]
        connection.executemany("INSERT INTO jobs (title, company, location, job_type, description, skills, instructions, is_sample, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", jobs)
    if connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        questions = [
            ("Programming", "Which Python keyword defines a function?", '["func", "def", "function", "method"]', 1, "Python uses def to begin a function definition.", 1, now_iso()),
            ("Technical", "Which SQL command reads records from a table?", '["GET", "OPEN", "SELECT", "FETCH TABLE"]', 2, "SELECT retrieves rows from one or more database tables.", 1, now_iso()),
            ("Aptitude", "A team completes 12 tasks in 3 days. At the same rate, how many in 5 days?", '["15", "18", "20", "24"]', 2, "12 divided by 3 is 4 tasks per day; 4 times 5 is 20.", 1, now_iso()),
            ("HR", "What is a strong way to answer a behavioral interview question?", '["Give a specific example and explain the outcome", "Only say what the interviewer wants", "Avoid answering directly", "List unrelated skills"]', 0, "A clear example with the situation, action, and outcome makes your answer concrete.", 1, now_iso()),
        ]
        connection.executemany("INSERT INTO questions (category, prompt, options, correct_answer, explanation, is_sample, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", questions)
    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DATABASE_PATH)
