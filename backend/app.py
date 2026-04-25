from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
CHAT_DIR = os.path.join(FRONTEND_DIR, "chat_dashboard")
LOGIN_DIR = os.path.join(FRONTEND_DIR, "login")
SIGNUP_DIR = os.path.join(FRONTEND_DIR, "signup_onboarding")

DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return send_from_directory(LOGIN_DIR, "code.html")


@app.route("/login")
def login():
    return send_from_directory(LOGIN_DIR, "code.html")


@app.route("/signup")
def signup():
    return send_from_directory(SIGNUP_DIR, "code.html")


@app.route("/chat")
def chat():
    return send_from_directory(CHAT_DIR, "index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is running",
        "chat_page": "/chat",
        "login_page": "/login",
        "signup_page": "/signup"
    })


@app.route("/api/students")
def get_students():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM students LIMIT 20")
        rows = cur.fetchall()
        conn.close()

        students = [dict(row) for row in rows]
        return jsonify(students)

    except Exception as e:
        return jsonify({
            "error": "Could not read students table",
            "details": str(e)
        }), 500


@app.route("/api/adviser", methods=["POST"])
def adviser():
    data = request.get_json() or {}

    question = data.get("question", "")
    student_id = data.get("student_id", 1)

    if not question:
        return jsonify({"reply": "Please ask a question first."}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cur.fetchone()
        conn.close()

        if student:
            student = dict(student)
            name = student.get("name", "student")
            year = student.get("year", "student")
            major = student.get("major", "Computer Science")
            completed = student.get("completed_courses", "No completed courses listed")

            reply = (
                f"Hi {name}. Based on your profile as a {year} {major} student, "
                f"and your completed courses: {completed}, here is my advice: "
                f"For your question, '{question}', you should focus on the next required "
                f"Computer Science, math, and general education courses in your curriculum. "
                f"Make sure prerequisites are completed before registering."
            )
        else:
            reply = (
                f"I could not find student ID {student_id}, but based on your question "
                f"'{question}', I recommend checking your CS curriculum, prerequisites, "
                f"and degree audit before choosing classes."
            )

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": "The adviser backend had an error.",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)