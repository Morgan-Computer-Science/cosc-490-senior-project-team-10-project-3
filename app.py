from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "student_advisor.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_student(student_id: int):
    conn = get_connection()
    row = conn.execute("""
        SELECT student_id, first_name, last_name, class_level, current_semester, credits_earned, status_note
        FROM students
        WHERE student_id = ?
    """, (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_progress(student_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT completed_course_code, completed_course_title, credits, term_completed
        FROM student_progress
        WHERE student_id = ?
        ORDER BY term_completed
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_semester_plan(semester_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            s.year_label,
            s.term_label,
            COALESCE(c.course_code, '[' || cc.placeholder_label || ']') AS item,
            COALESCE(c.course_title, cc.placeholder_label) AS title,
            cc.requirement_type
        FROM curriculum_courses cc
        JOIN semesters s ON s.semester_id = cc.semester_id
        LEFT JOIN courses c ON c.course_id = cc.course_id
        WHERE cc.semester_id = ?
        ORDER BY cc.curriculum_id
    """, (semester_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_elective_choices(group_code: str):
    conn = get_connection()
    rows = conn.execute("""
        SELECT course_code, course_title, credits, category, elective_group
        FROM courses
        WHERE elective_group = ?
        ORDER BY course_code
    """, (group_code,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def build_adviser_response(student: dict, progress: list, question: str):
    q = question.lower()
    first_name = student["first_name"]
    completed_codes = {row["completed_course_code"] for row in progress}

    if "gpa" in q:
        return (
            f"{first_name}, your GPA is not stored in this demo database yet. "
            f"You currently have {student['credits_earned']} earned credits and you are listed as a "
            f"{student['class_level']} in semester {student['current_semester']}."
        )

    if "progress" in q or "completed" in q:
        if not progress:
            return f"{first_name} has no completed-course records yet."
        sample = ", ".join([row["completed_course_code"] for row in progress[:6]])
        return (
            f"{first_name}, you have {len(progress)} completed courses recorded so far. "
            f"Some of them are {sample}."
        )

    if "elective" in q or "group a" in q:
        electives = get_elective_choices("A")
        if not electives:
            return "I could not find any Group A electives in the database."
        sample = ", ".join([row["course_code"] for row in electives[:6]])
        return f"Some Group A elective choices are {sample}."

    if "classes" in q or "take" in q or "schedule" in q or "semester" in q or "plan" in q:
        next_semester = min(student["current_semester"] + 1, 8)
        plan = get_semester_plan(next_semester)

        recommended = []
        for row in plan:
            item = row["item"]
            if not item.startswith("[") and item not in completed_codes:
                recommended.append(item)

        if recommended:
            sample = ", ".join(recommended[:5])
            return f"{first_name}, based on your current record, a good next-semester plan is: {sample}."

        return (
            f"{first_name}, you are close to finishing the standard sequence. "
            f"You should focus on any remaining electives and graduation requirements."
        )

    return f"Hi {first_name}, I can help with class recommendations, semester planning, electives, and progress tracking."


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Backend is running. Open index.html separately in your browser."
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is running"})


@app.route("/api/students", methods=["GET"])
def students():
    conn = get_connection()
    rows = conn.execute("""
        SELECT student_id, first_name, last_name, class_level, current_semester, credits_earned, status_note
        FROM students
        ORDER BY student_id
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/student/<int:student_id>", methods=["GET"])
def student_detail(student_id):
    student = get_student(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    progress = get_student_progress(student_id)
    return jsonify({
        "student": student,
        "progress": progress
    })


@app.route("/api/semester/<int:semester_id>", methods=["GET"])
def semester_detail(semester_id):
    return jsonify(get_semester_plan(semester_id))


@app.route("/api/electives/<group_code>", methods=["GET"])
def electives(group_code):
    return jsonify(get_elective_choices(group_code.upper()))


@app.route("/api/adviser", methods=["POST"])
def adviser():
    data = request.get_json(silent=True) or {}

    student_id = data.get("student_id", 1)
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"reply": "Please enter a question for the adviser."}), 400

    student = get_student(student_id)
    if not student:
        return jsonify({"reply": "Student not found."}), 404

    progress = get_student_progress(student_id)
    reply = build_adviser_response(student, progress, question)

    return jsonify({
        "reply": reply,
        "student": student,
        "progress_count": len(progress)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)