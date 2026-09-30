import os
import sys
import sqlite3
import tempfile
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Base directory for api
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# If running at root rather than api subfolder, fallback
if not os.path.exists(TEMPLATE_DIR):
    TEMPLATE_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
if not os.path.exists(STATIC_DIR):
    STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
)
app.secret_key = os.environ.get("SECRET_KEY", "brainbox-demo-secret-key-change-me")

# Expose both app and handler for all Vercel WSGI runtimes
handler = app

def get_database_path():
    if os.environ.get("DATABASE_PATH"):
        return os.environ.get("DATABASE_PATH")
    
    # On Linux (Vercel Serverless / Lambda / Render), use /tmp/brainbox.db
    if sys.platform != "win32" or os.environ.get("VERCEL"):
        return os.path.join(tempfile.gettempdir(), "brainbox.db")
    
    # Local Windows development
    return os.path.join(os.path.dirname(BASE_DIR), "brainbox.db")

SUBJECTS = {
    "Python": ["Basics", "Functions", "OOP"],
    "Web Development": ["HTML", "CSS"],
    "Database": ["SQL", "Database Basics"],
}

QUESTIONS = [
    # Python - Basics
    ("Python", "Basics", "Which keyword is used to define a function in Python?", "def", "function", "fun", "define", "def"),
    ("Python", "Basics", "Which data type stores True or False values in Python?", "Boolean", "String", "List", "Float", "Boolean"),
    ("Python", "Basics", "What is the output of print(2 ** 3) in Python?", "8", "6", "9", "5", "8"),
    ("Python", "Basics", "Which symbol is used for single-line comments in Python?", "#", "//", "/*", "--", "#"),
    
    # Python - Functions
    ("Python", "Functions", "Which statement returns a value from a function?", "return", "print", "break", "continue", "return"),
    ("Python", "Functions", "Which symbol is used to call a function?", "()", "[]", "{}", "<>", "()"),
    ("Python", "Functions", "What keyword is used to create an anonymous/inline function in Python?", "lambda", "def", "func", "inline", "lambda"),
    ("Python", "Functions", "What is the return value of a Python function that does not have an explicit return statement?", "None", "0", "False", "undefined", "None"),

    # Python - OOP
    ("Python", "OOP", "Which concept allows a class to inherit features from another class?", "Inheritance", "Compilation", "Iteration", "Indexing", "Inheritance"),
    ("Python", "OOP", "What is the first parameter typically passed to instance methods in Python?", "self", "this", "cls", "super", "self"),
    ("Python", "OOP", "Which special method is automatically called when a new object is instantiated?", "__init__", "__new__", "__start__", "__main__", "__init__"),

    # Web Development - HTML
    ("Web Development", "HTML", "Which HTML tag is used for the largest main heading?", "h1", "p", "head", "title", "h1"),
    ("Web Development", "HTML", "Which attribute provides alternative text for an image?", "alt", "src", "href", "title", "alt"),
    ("Web Development", "HTML", "Which HTML element is used to insert a line break?", "<br>", "<lb>", "<break>", "<hr>", "<br>"),
    ("Web Development", "HTML", "Which tag is used to create a hyperlink?", "<a>", "<link>", "<href>", "<nav>", "<a>"),

    # Web Development - CSS
    ("Web Development", "CSS", "Which CSS property changes text color?", "color", "font-style", "background", "text-decoration", "color"),
    ("Web Development", "CSS", "Which symbol is used for a CSS class selector?", ".", "#", "@", "$", "."),
    ("Web Development", "CSS", "Which CSS property is used to control spacing inside an element border?", "padding", "margin", "spacing", "border-spacing", "padding"),
    ("Web Development", "CSS", "Which display property value creates a flexible layout container?", "flex", "block", "inline", "table", "flex"),

    # Database - SQL
    ("Database", "SQL", "Which SQL command is used to retrieve data from a database?", "SELECT", "GET", "FETCHALL", "OPEN", "SELECT"),
    ("Database", "SQL", "Which SQL command adds a new row to a table?", "INSERT", "ADD", "UPDATE", "CREATE", "INSERT"),
    ("Database", "SQL", "Which clause is used to filter records in a SQL SELECT statement?", "WHERE", "FILTER", "HAVING", "ORDER BY", "WHERE"),
    ("Database", "SQL", "Which SQL keyword is used to sort the result set?", "ORDER BY", "SORT BY", "GROUP BY", "ARRANGE", "ORDER BY"),

    # Database - Database Basics
    ("Database", "Database Basics", "What is a primary key used for in a relational database?", "Uniquely identifying records", "Sorting only", "Deleting tables", "Formatting data", "Uniquely identifying records"),
    ("Database", "Database Basics", "What does DBMS stand for?", "Database Management System", "Data Base Multi Server", "Digital Binary Management Service", "Data Backup Management Software", "Database Management System"),
    ("Database", "Database Basics", "Which key establishes a link between data in two tables?", "Foreign Key", "Super Key", "Candidate Key", "Secondary Key", "Foreign Key"),
]

def get_db():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student'
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        percentage REAL NOT NULL,
        taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_answer TEXT,
        correct_answer TEXT NOT NULL,
        FOREIGN KEY(attempt_id) REFERENCES attempts(id),
        FOREIGN KEY(question_id) REFERENCES questions(id)
    )""")

    admin = cur.execute("SELECT id FROM users WHERE email = ?", ("admin@brainbox.local",)).fetchone()
    if not admin:
        cur.execute(
            "INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
            ("BrainBox Admin", "admin@brainbox.local", "admin123", "admin")
        )

    count = cur.execute("SELECT COUNT(*) AS c FROM questions").fetchone()["c"]
    if count == 0:
        cur.executemany("""INSERT INTO questions
            (subject,topic,question,option_a,option_b,option_c,option_d,correct_answer)
            VALUES (?,?,?,?,?,?,?,?)""", QUESTIONS)
    conn.commit()
    conn.close()

def ensure_db_initialized():
    try:
        conn = get_db()
        table = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'").fetchone()
        conn.close()
        if not table:
            init_db()
    except Exception:
        try:
            init_db()
        except Exception:
            pass

@app.before_request
def auto_init_db():
    if not getattr(app, "_db_initialized", False):
        ensure_db_initialized()
        app._db_initialized = True

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_common():
    return {"subjects": SUBJECTS}

@app.route("/health")
def health():
    return {"status": "ok", "app": "BrainBox", "database": get_database_path()}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Please fill all fields.", "danger")
            return render_template("register.html")
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                (name, email, password)
            )
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "danger")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    attempts = conn.execute(
        "SELECT * FROM attempts WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()
    stats = conn.execute(
        """SELECT COUNT(*) AS attempts,
                  COALESCE(ROUND(AVG(percentage),1),0) AS avg_score
           FROM attempts WHERE user_id=?""",
        (session["user_id"],)
    ).fetchone()
    weak = conn.execute(
        """SELECT subject, topic, ROUND(AVG(percentage),1) AS avg_percentage
           FROM attempts WHERE user_id=?
           GROUP BY subject, topic
           HAVING AVG(percentage) < 60
           ORDER BY avg_percentage ASC""",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", attempts=attempts, stats=stats, weak=weak)

@app.route("/quiz")
@login_required
def quiz():
    subject = request.args.get("subject", "").strip()
    topic = request.args.get("topic", "").strip()
    if subject not in SUBJECTS or topic not in SUBJECTS[subject]:
        flash("Please select a valid subject and topic.", "warning")
        return redirect(url_for("dashboard"))
    conn = get_db()
    questions = conn.execute(
        "SELECT * FROM questions WHERE subject=? AND topic=? ORDER BY id",
        (subject, topic)
    ).fetchall()
    conn.close()
    if not questions:
        flash("No questions are available for this topic yet.", "warning")
        return redirect(url_for("dashboard"))
    return render_template("quiz.html", questions=questions, subject=subject, topic=topic)

@app.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    subject = request.form.get("subject", "").strip()
    topic = request.form.get("topic", "").strip()
    question_ids = request.form.getlist("question_ids")
    if not question_ids:
        flash("No questions submitted.", "warning")
        return redirect(url_for("dashboard"))
    conn = get_db()
    questions = []
    for qid in question_ids:
        q = conn.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()
        if q:
            questions.append(q)
    if not questions:
        conn.close()
        flash("No valid questions found for submission.", "warning")
        return redirect(url_for("dashboard"))
    score = 0
    selections = []
    for q in questions:
        selected = request.form.get(f"q_{q['id']}", "").strip()
        if selected == q["correct_answer"]:
            score += 1
        selections.append((q["id"], selected, q["correct_answer"]))
    total = len(questions)
    percentage = round((score / total) * 100, 1) if total else 0
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO attempts (user_id,subject,topic,score,total,percentage)
           VALUES (?,?,?,?,?,?)""",
        (session["user_id"], subject, topic, score, total, percentage)
    )
    attempt_id = cur.lastrowid
    cur.executemany(
        """INSERT INTO results (attempt_id,question_id,selected_answer,correct_answer)
           VALUES (?,?,?,?)""",
        [(attempt_id, qid, selected, correct) for qid, selected, correct in selections]
    )
    conn.commit()
    conn.close()
    return redirect(url_for("result", attempt_id=attempt_id))

@app.route("/result/<int:attempt_id>")
@login_required
def result(attempt_id):
    conn = get_db()
    attempt = conn.execute(
        "SELECT * FROM attempts WHERE id=? AND user_id=?",
        (attempt_id, session["user_id"])
    ).fetchone()
    if not attempt:
        conn.close()
        flash("Result not found.", "danger")
        return redirect(url_for("dashboard"))
    details = conn.execute(
        """SELECT r.*, q.question, q.option_a, q.option_b, q.option_c, q.option_d
           FROM results r LEFT JOIN questions q ON q.id=r.question_id
           WHERE r.attempt_id=?""",
        (attempt_id,)
    ).fetchall()
    conn.close()
    return render_template("result.html", attempt=attempt, details=details)

@app.route("/admin")
@login_required
@admin_required
def admin():
    conn = get_db()
    questions = conn.execute("SELECT * FROM questions ORDER BY subject, topic, id").fetchall()
    users = conn.execute("SELECT id,name,email,role FROM users ORDER BY id DESC").fetchall()
    attempts = conn.execute(
        """SELECT a.*, u.name FROM attempts a
           JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 20"""
    ).fetchall()
    conn.close()
    return render_template("admin.html", questions=questions, users=users, attempts=attempts)

@app.route("/admin/add-question", methods=["POST"])
@login_required
@admin_required
def add_question():
    subject = request.form.get("subject", "").strip()
    topic = request.form.get("topic", "").strip()
    question = request.form.get("question", "").strip()
    options = [request.form.get(f"option_{x}", "").strip() for x in "abcd"]
    correct = request.form.get("correct", "").strip()
    if subject not in SUBJECTS or topic not in SUBJECTS[subject] or not question or not all(options) or correct not in options:
        flash("Please enter valid question details. Correct answer must match one of the options exactly.", "danger")
        return redirect(url_for("admin"))
    conn = get_db()
    conn.execute(
        """INSERT INTO questions
        (subject,topic,question,option_a,option_b,option_c,option_d,correct_answer)
        VALUES (?,?,?,?,?,?,?,?)""",
        (subject, topic, question, *options, correct)
    )
    conn.commit()
    conn.close()
    flash("Question added successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/delete-question/<int:qid>", methods=["POST"])
@login_required
@admin_required
def delete_question(qid):
    conn = get_db()
    conn.execute("DELETE FROM questions WHERE id=?", (qid,))
    conn.commit()
    conn.close()
    flash("Question deleted successfully.", "success")
    return redirect(url_for("admin"))

@app.route("/init")
def initialize():
    init_db()
    flash("Database initialized successfully.", "success")
    return redirect(url_for("home"))

@app.errorhandler(500)
def server_error(e):
    import traceback
    tb = traceback.format_exc()
    try:
        return render_template("index.html"), 200
    except Exception:
        return f"<h3>BrainBox Server Error</h3><pre>{tb}</pre>", 500

@app.errorhandler(404)
def not_found(e):
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
