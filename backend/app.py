from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from agent import run_advisor_agents
import os

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
        "adviser_endpoint": "/api/adviser"
    })


@app.route("/api/adviser", methods=["POST"])
def adviser():
    data = request.get_json() or {}

    student_id = data.get("student_id", 1)
    question = data.get("question", "").strip()

    file_name = data.get("file_name", "")
    file_text = data.get("file_text", "")

    if not question:
        return jsonify({
            "reply": "Please ask a question first."
        }), 400

    try:
        if file_text:
            question = f"{question}\n\nAttached file name: {file_name}\n\nAttached file content:\n{file_text}"

        reply = run_advisor_agents(student_id, question)

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        return jsonify({
            "reply": "The advising system had an error.",
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Route not found",
        "message": "Check that you are using /chat, /login, /signup, /api/health, or /api/adviser."
    }), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )