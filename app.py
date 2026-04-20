from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="chat_dashboard")
CORS(app)

def advisor_agent(message):
    return f"Advisor says: Based on your question '{message}', here’s some guidance."

@app.route("/", methods=["GET"])
def home():
    return send_from_directory("chat_dashboard", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "No message provided."}), 400

    return jsonify({"reply": advisor_agent(message)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)