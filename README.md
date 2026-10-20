# Web Application Exercise

A mobile-friendly lost and found app for campus users to report missing items, share discoveries, and help belongings find their way home.

See [instructions.md](instructions.md) for the full course assignment instructions.

## Setup and run locally

1. Install Python 3.10 or newer and MongoDB Community Server, or use a MongoDB Atlas database.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install the application and test dependencies:
   ```bash
   python -m pip install -r requirements-dev.txt
   ```
4. Copy `env.example` to `.env`. Set `MONGO_URI` and `MONGO_DBNAME` to your local or team development database, and replace `SECRET_KEY` with a long random value. Do not commit `.env` or share production credentials.
5. Start the app:
   ```bash
   flask --app app run
   ```
6. Open http://127.0.0.1:5000/home. Posts are loaded from the configured MongoDB database. No sample posts are inserted automatically.

Use a dedicated test database for local manual testing. Automated tests use mongomock and never connect to MongoDB.

## Authentication and ownership status

Login and signup screens are currently static and do not authenticate users. Until real account authentication is integrated, the app assigns new posts to a random owner ID stored in Flask's signed browser session. This gives direct edit and delete requests a server-side ownership check, but it is temporary browser-level ownership: clearing the browser session loses access to those controls, and it does not identify a person or provide account recovery. Posts created before owner IDs were added remain visible but read-only.

All post writes use CSRF tokens. Set `SESSION_COOKIE_SECURE=true` when serving the app over HTTPS. Use a private, stable `SECRET_KEY` in every non-local environment.

## Tests

Run the focused post tests with:

```bash
python -m pytest
```

The tests inject a fresh mongomock collection and do not modify a shared MongoDB database.

## Course workflow and AI attribution

After cloning, run the required course setup from the repository root:

```bash
python3 .automations/setup.py
```

Approve the repository hooks in your AI coding tools as described by the setup script. The `.automations` files are instructor-managed and must not be modified.

## User stories and task boards

Add the team's GitHub Issues and Projects links here when they are available.
