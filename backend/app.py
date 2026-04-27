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
        "message": "Backend is running"
    })


@app.route("/api/adviser", methods=["POST"])
def adviser():
    data = request.get_json() or {}

    question = data.get("question", "").strip()

    if not question:
        return jsonify({"reply": "Please ask a question first."}), 400

    reply = (
        f"I can help you with academic advising, course planning, prerequisites, "
        f"registration guidance, graduation progress, and semester scheduling.\n\n"
        f"Based on your question: '{question}', I recommend checking your completed "
        f"CS courses, math requirements, general education classes, and prerequisites "
        f"before choosing your next semester schedule."
    )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)