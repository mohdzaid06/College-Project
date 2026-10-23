# Student Placement Preparation System

A beginner-friendly college project that combines a React career-preparation dashboard with a Flask JSON API and SQLite database. The listings bundled with the project are fictional samples for practice; they are not real or currently open vacancies.

## Features

- Responsive home page and searchable, filterable job listings with detail pages.
- Student registration and login. Passwords are hashed on the server; the browser receives an HttpOnly signed session cookie.
- Practice questions in programming, aptitude, technical, and HR categories. Flask calculates quiz scores and stores attempts for logged-in students.
- Personal job application tracker with Saved, Applied, Interview, Offered, and Rejected statuses. Every query is scoped to the signed-in student.
- Admin-only create, edit, and delete tools for job listings and practice questions. The API checks the role on every request.
- SQLite schema and fictional sample data are created automatically and safely on first startup.

## Technology and folder structure

- React, JavaScript, Vite, React Router, and CSS for the user interface.
- Flask and Flask-CORS for the REST API. REST is a common pattern where the browser requests named URLs and receives JSON data.
- SQLite for local storage. A table is like a spreadsheet; a primary key identifies each row, and a foreign key connects related tables.
- Cookie-based sessions for this local project. The server signs the cookie, marks it HttpOnly, and keeps the user ID in the session. This avoids storing an authentication token in JavaScript-accessible local storage. It is a teaching setup, not a production deployment configuration.

```text
backend/
  app.py             Flask routes, validation, sessions, permissions
  database.py        SQLite connection, schema, sample data
  create_admin.py    Secure local admin setup from environment variables
  tests/             Automated API tests
frontend/
  src/App.jsx        Routes and authentication state
  src/components/    Navigation and shared UI
  src/pages/         Home, jobs, login, dashboard, quiz, admin
  src/services/api.js Central JSON API client (sends session cookies)
  src/styles.css     Responsive visual design
docs/                Project report, diagrams, database, API, and test notes
```

## Prerequisites

- macOS with Python 3.9 or newer, Node.js 20 or newer, and npm.
- Internet access for the first dependency installation.

## Setup and run on macOS

Open two VS Code terminals in this project folder.

### 1. Set up and start Flask

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python database.py
python app.py
```

The virtual environment keeps this project's Python packages separate from other projects. `python database.py` creates `backend/placement.db`; Flask also initializes the schema on startup. The database is ignored by Git. Keep the backend terminal running at `http://127.0.0.1:5000`.

### 2. Set up and start React

In a second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://127.0.0.1:5173`). React sends API requests to `http://127.0.0.1:5000/api` and includes the session cookie. Set `VITE_API_URL` in `frontend/.env.local` only if the API uses a different local address; restart Vite after changing it.

### 3. Create a local administrator (optional)

Create a strong password of at least 12 characters and provide it only in the backend terminal. These variables are read by the setup script and are not placed in source code:

```sh
cd backend
source .venv/bin/activate
export ADMIN_EMAIL='admin@example.test'
printf 'Enter a local admin password (12+ characters): '
read -s ADMIN_PASSWORD
printf '\n'
export ADMIN_PASSWORD
python create_admin.py
unset ADMIN_EMAIL ADMIN_PASSWORD
```

Then log into the app with that email/password. The admin page is at `/admin`. Do not reuse a real account password. For a persistent local secret, set `SECRET_KEY` in the backend terminal before running `python app.py`; the fallback key is intended only for local development.

## URLs and API

- Frontend: `http://127.0.0.1:5173`
- Backend health check: `http://127.0.0.1:5000/api/health`
- The API is documented in [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md#api-documentation).

## Test and build

From the project folder:

```sh
cd backend
source .venv/bin/activate
python -m unittest discover -s tests -v
cd ../frontend
npm run build
```

The backend tests use temporary databases, so they do not alter your local sample data. A successful `npm run build` checks that Vite can compile the React app. See the report for the actual checks run during project setup.

## Troubleshooting

- **`ModuleNotFoundError: flask`:** activate the backend virtual environment and run `python -m pip install -r requirements.txt`.
- **Frontend says it cannot reach the API:** make sure the Flask terminal is running; visit `/api/health`; confirm Vite uses port 5173 and the API URL is `http://127.0.0.1:5000/api`.
- **CORS message in the browser:** this project only allows the configured local frontend origin. Set `FRONTEND_ORIGIN` to the exact Vite origin, restart Flask, and keep `supports_credentials` enabled in the code.
- **Port already in use:** stop the other process or run Flask with `PORT=5001 python app.py`, then set `VITE_API_URL=http://127.0.0.1:5001/api` and restart Vite.
- **Login appears lost after restarting:** sessions are stored in the browser cookie; log in again. Student accounts and progress remain in SQLite.
- **Admin page does not show:** create/promote an account using the admin setup command, then log out and back in.

## Known limitations

- The included job listings and questions are fictional demonstrations; there are no live vacancy feeds or employer applications.
- The app is intended for local demonstration. Before a public deployment, add HTTPS, a strong managed secret, secure cookie settings, CSRF defenses, account recovery, rate limiting, and a production hosting configuration.
- The database is a single local SQLite file and is not configured for simultaneous multi-server production use.
- Styling uses Google Fonts when online and falls back to system fonts when offline.

## Beginner concepts

- **Frontend:** the part in the browser that the student sees and uses.
- **Backend:** the Flask program that validates requests, checks permissions, and reads or updates data.
- **API / route:** an address such as `/api/jobs` that the frontend can request to perform one action.
- **HTTP request:** the browser's message to the backend; JSON is the structured data format used in those messages.
- **Authentication:** checking who has logged in. **Authorization:** checking what that signed-in person may do.
- **CRUD:** create, read, update, and delete records.

## Viva questions

1. **Why use Flask with SQLite?** Flask keeps the API small and understandable, and SQLite stores project data in a local file without needing a separate database server.
2. **Why hash passwords?** Hashing stores a one-way password verifier, so the database does not contain the user's original password.
3. **How are student applications private?** Each API query uses the authenticated session's user ID, and update statements match both the application ID and that user ID.
