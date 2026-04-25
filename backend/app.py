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
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"reply": "Please ask a question first."}), 400

    q = question.lower()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Course search
        cur.execute("""
            SELECT course_code, course_title, credits, category, elective_group
            FROM courses
            WHERE lower(course_code) LIKE ?
               OR lower(course_title) LIKE ?
               OR lower(category) LIKE ?
            ORDER BY course_code
        """, (f"%{q}%", f"%{q}%", f"%{q}%"))

        course_rows = cur.fetchall()

        # Semester/year search
        semester_number = None
        if "freshman" in q or "first semester" in q:
            semester_number = 1
        elif "second semester" in q:
            semester_number = 2
        elif "sophomore" in q or "third semester" in q:
            semester_number = 3
        elif "fourth semester" in q:
            semester_number = 4
        elif "junior" in q or "fifth semester" in q:
            semester_number = 5
        elif "sixth semester" in q:
            semester_number = 6
        elif "senior" in q or "seventh semester" in q:
            semester_number = 7
        elif "eighth semester" in q:
            semester_number = 8

        if semester_number:
            cur.execute("""
                SELECT 
                    s.year_label,
                    s.term_label,
                    c.course_code,
                    c.course_title,
                    c.credits,
                    cc.placeholder_label,
                    cc.requirement_type,
                    cc.choice_group
                FROM curriculum_courses cc
                JOIN semesters s ON cc.semester_id = s.semester_id
                LEFT JOIN courses c ON cc.course_id = c.course_id
                WHERE s.semester_number = ?
                ORDER BY cc.curriculum_id
            """, (semester_number,))

            rows = cur.fetchall()
            conn.close()

            items = []
            for row in rows:
                if row["course_code"]:
                    items.append(f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)")
                else:
                    items.append(f"- {row['placeholder_label']}")

            reply = (
                f"For {rows[0]['year_label']} {rows[0]['term_label']}, your recommended curriculum is:\n\n"
                + "\n".join(items)
            )

            return jsonify({"reply": reply})

        # Elective group search
        for group in ["a", "b", "c", "d"]:
            if f"group {group}" in q:
                cur.execute("""
                    SELECT course_code, course_title, credits
                    FROM courses
                    WHERE lower(elective_group) = ?
                    ORDER BY course_code
                """, (group,))

                rows = cur.fetchall()
                conn.close()

                items = [
                    f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)"
                    for row in rows
                ]

                reply = f"Here are the Group {group.upper()} electives:\n\n" + "\n".join(items)
                return jsonify({"reply": reply})

        # If course matches were found
        if course_rows:
            conn.close()

            items = [
                f"- {row['course_code']}: {row['course_title']} "
                f"({row['credits']} credits, {row['category']}"
                f"{', Group ' + row['elective_group'] if row['elective_group'] else ''})"
                for row in course_rows
            ]

            reply = "I found these matching courses in the database:\n\n" + "\n".join(items)
            return jsonify({"reply": reply})

        # General curriculum response
        cur.execute("""
            SELECT 
                s.year_label,
                s.term_label,
                c.course_code,
                c.course_title,
                cc.placeholder_label,
                cc.requirement_type
            FROM curriculum_courses cc
            JOIN semesters s ON cc.semester_id = s.semester_id
            LEFT JOIN courses c ON cc.course_id = c.course_id
            ORDER BY s.semester_number, cc.curriculum_id
        """)

        rows = cur.fetchall()
        conn.close()

        reply = (
            "I can answer questions using the backend curriculum database. "
            "Try asking things like:\n\n"
            "- What classes should I take freshman first semester?\n"
            "- What classes should I take junior year?\n"
            "- Show me Group A electives\n"
            "- What is COSC 354?\n"
            "- What courses are required for senior year?"
        )

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({
            "reply": "The adviser backend had an error.",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)