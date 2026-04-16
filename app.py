from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def advisor_agent(message):
    return f"Advisor says: Based on your question '{message}', here’s some guidance."

@app.route("/", methods=["GET"])
def home():
    return "Backend is running."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "No message provided."}), 400

    return jsonify({"reply": advisor_agent(message)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)