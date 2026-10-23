"""Create or promote a local administrator using environment variables."""

import os
import sys

from werkzeug.security import generate_password_hash

from database import connect_db, init_db, now_iso


def main():
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("ADMIN_PASSWORD", "")
    name = os.environ.get("ADMIN_NAME", "Local Administrator").strip()
    if not email or len(password) < 12:
        print("Set ADMIN_EMAIL and ADMIN_PASSWORD (at least 12 characters) in your terminal environment.", file=sys.stderr)
        return 1
    init_db()
    db = connect_db()
    row = db.execute("SELECT id FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
    if row:
        db.execute("UPDATE users SET name = ?, password_hash = ?, role = 'admin' WHERE id = ?", (name, generate_password_hash(password, method="pbkdf2:sha256:600000"), row["id"]))
    else:
        db.execute("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, 'admin', ?)", (name, email, generate_password_hash(password, method="pbkdf2:sha256:600000"), now_iso()))
    db.commit()
    db.close()
    print("Local administrator account is ready for:", email)
    return 0


if __name__ == "__main__":
    sys.exit(main())
