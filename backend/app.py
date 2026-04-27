from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from agent import run_advisor_agents
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
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"reply": "Please ask a question first."}), 400

    try:
        reply = run_advisor_agents(question)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": "The advisor agent had an error.",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)