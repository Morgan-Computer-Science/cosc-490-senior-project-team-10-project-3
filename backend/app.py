from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import traceback

# Try to use the richer advising engine if available.
# If advising_ai.py depends on packages that are not installed,
# the backend will still work in database mode.
try:
    from advising_ai import AcademicAdvisor
    advisor_engine = AcademicAdvisor()
    ADVISOR_ENGINE_AVAILABLE = True
    ADVISOR_ENGINE_ERROR = None
except Exception as e:
    advisor_engine = None
    ADVISOR_ENGINE_AVAILABLE = False
    ADVISOR_ENGINE_ERROR = str(e)

app = Flask(__name__)

# Allow frontend requests to the API
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")


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


def build_database_reply(student: dict, progress: list, question: str):
    q = question.lower()
    first_name = student["first_name"]
    completed_codes = {row["completed_course_code"] for row in progress}

    if "gpa" in q:
        return (
            f"{first_name}, your GPA is not stored in this demo database yet. "
            f"You currently have {student['credits_earned']} earned credits and are listed as a "
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

    if "group b" in q:
        electives = get_elective_choices("B")
        if not electives:
            return "I could not find any Group B electives in the database."
        sample = ", ".join([row["course_code"] for row in electives[:6]])
        return f"Some Group B elective choices are {sample}."

    if "group c" in q:
        electives = get_elective_choices("C")
        if not electives:
            return "I could not find any Group C electives in the database."
        sample = ", ".join([row["course_code"] for row in electives[:6]])
        return f"Some Group C elective choices are {sample}."

    if "group d" in q:
        electives = get_elective_choices("D")
        if not electives:
            return "I could not find any Group D electives in the database."
        sample = ", ".join([row["course_code"] for row in electives[:6]])
        return f"Some Group D elective choices are {sample}."

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

    return (
        f"Hi {first_name}, I can help with class recommendations, semester planning, "
        f"electives, and progress tracking."
    )


def build_enhanced_reply(student: dict, progress: list, question: str):
    base_reply = build_database_reply(student, progress, question)

    if not ADVISOR_ENGINE_AVAILABLE or advisor_engine is None:
        return base_reply

    q = question.lower()
    extra_parts = []

    try:
        if any(word in q for word in ["degree", "graduate", "graduation", "credits", "remaining"]):
            metrics = advisor_engine.calculate_degree_progress()
            extra_parts.append(
                f" Demo advisor summary: about {metrics['total_credits']} completed credits, "
                f"{metrics['remaining_credits']} remaining, and an estimated GPA of {metrics['gpa']:.2f}."
            )

        if any(word in q for word in ["schedule", "conflict", "availability", "work", "time"]):
            schedules = advisor_engine.find_conflict_free_schedules(question)
            if schedules:
                best = schedules[0]
                extra_parts.append(
                    f" Suggested schedule option: {best['name']} with "
                    f"{', '.join(best['courses'])}. Reason: {best['reasoning']}."
                )

        if "availability" in q:
            availability_text = advisor_engine.format_availability_string()
            extra_parts.append(" Weekly availability snapshot:\n" + availability_text)

    except Exception:
        return base_reply

    if extra_parts:
        return base_reply + "\n\n" + "".join(extra_parts)

    return base_reply


@app.route("/", methods=["GET"])
def home():
    response = {
        "message": "Backend is running. Open index.html separately in your browser.",
        "adviser_endpoint": "/api/adviser",
        "students_endpoint": "/api/students",
        "health_endpoint": "/api/health",
        "advisor_engine_available": ADVISOR_ENGINE_AVAILABLE
    }

    if not ADVISOR_ENGINE_AVAILABLE:
        response["advisor_engine_note"] = "AcademicAdvisor could not be loaded. Database mode is still active."
        response["advisor_engine_error"] = ADVISOR_ENGINE_ERROR

    return jsonify(response)


@app.route("/api/health", methods=["GET"])
def health():
    data = {
        "status": "ok",
        "message": "Backend is running",
        "advisor_engine_available": ADVISOR_ENGINE_AVAILABLE,
        "db_path": DB_PATH
    }

    if not ADVISOR_ENGINE_AVAILABLE:
        data["advisor_engine_note"] = "AcademicAdvisor not loaded"
        data["advisor_engine_error"] = ADVISOR_ENGINE_ERROR

    return jsonify(data)


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


@app.route("/api/adviser", methods=["POST", "OPTIONS"])
def adviser():
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200

    try:
        data = request.get_json(silent=True) or {}

        question = str(data.get("question") or data.get("message") or "").strip()

        raw_student_id = data.get("student_id", 1)
        try:
            student_id = int(raw_student_id)
        except (TypeError, ValueError):
            student_id = 1

        if not question:
            return jsonify({"reply": "Please enter a question for the adviser."}), 400

        student = get_student(student_id)
        if not student:
            return jsonify({"reply": f"Student {student_id} not found."}), 404

        progress = get_student_progress(student_id)
        reply = build_enhanced_reply(student, progress, question)

        return jsonify({
            "reply": reply,
            "student": student,
            "progress_count": len(progress),
            "advisor_engine_available": ADVISOR_ENGINE_AVAILABLE
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "reply": "The adviser hit a server error.",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)