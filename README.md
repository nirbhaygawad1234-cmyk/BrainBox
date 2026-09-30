# BrainBox – Personalized Quiz and Revision Management System

A simple full-stack academic quiz application built with HTML, CSS, Python Flask and SQLite.

## Features
- Student registration and login
- Subject/topic-wise quizzes
- Automatic scoring
- Answer review
- Attempt history
- Performance-based weak-topic identification
- Revision suggestions
- Admin question management
- SQLite database

## Demo admin account
Email: `admin@brainbox.local`
Password: `admin123`

Change these credentials before using the project for real users.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Deploy on Render

Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn app:app`

The application uses SQLite for this student project. For a production system, use a hosted database such as PostgreSQL and environment variables for secrets.

## Project structure

- `app.py` – Flask backend and database logic
- `templates/` – HTML pages
- `static/style.css` – CSS styling
- `requirements.txt` – Python dependencies
- `README.md` – project documentation
