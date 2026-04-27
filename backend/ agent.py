import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")


def query_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def curriculum_agent(question):
    courses = query_db("""
        SELECT *
        FROM courses
        ORDER BY semester_id
    """)

    if not courses:
        return "I could not find curriculum course data in the database."

    reply = "Here are the required curriculum courses I found:\n\n"

    for course in courses:
        code = course.get("course_code", "Unknown Code")
        name = course.get("course_name", "Unknown Course")
        credits = course.get("credits", "N/A")
        semester = course.get("semester_id", "N/A")

        reply += f"- Semester {semester}: {code} - {name} ({credits} credits)\n"

    return reply


def student_progress_agent(student_id):
    student = query_db("""
        SELECT *
        FROM students
        WHERE id = ?
    """, (student_id,))

    if not student:
        return "I could not find that student in the database."

    student = student[0]

    completed = query_db("""
        SELECT c.*
        FROM completed_courses cc
        JOIN courses c ON cc.course_id = c.id
        WHERE cc.student_id = ?
    """, (student_id,))

    reply = f"Student Progress Report for {student.get('name', 'Student')}:\n\n"
    reply += f"- Year: {student.get('year', 'Unknown')}\n"
    reply += f"- GPA: {student.get('gpa', 'Unknown')}\n\n"

    reply += "Completed Courses:\n"

    if completed:
        for course in completed:
            reply += f"- {course.get('course_code')}: {course.get('course_name')}\n"
    else:
        reply += "- No completed courses found.\n"

    return reply


def registration_planner_agent(student_id):
    completed = query_db("""
        SELECT c.course_code
        FROM completed_courses cc
        JOIN courses c ON cc.course_id = c.id
        WHERE cc.student_id = ?
    """, (student_id,))

    completed_codes = {course["course_code"] for course in completed}

    all_courses = query_db("""
        SELECT *
        FROM courses
        ORDER BY semester_id
    """)

    remaining = [
        course for course in all_courses
        if course.get("course_code") not in completed_codes
    ]

    if not remaining:
        return "This student appears to have completed all listed curriculum courses."

    next_courses = remaining[:5]

    reply = "Recommended classes for next semester:\n\n"

    for course in next_courses:
        reply += (
            f"- {course.get('course_code')}: "
            f"{course.get('course_name')} "
            f"({course.get('credits', 'N/A')} credits)\n"
        )

    reply += "\nThese are recommended because they are the next missing courses in the curriculum sequence."

    return reply


def policy_agent(question):
    q = question.lower()

    if "prerequisite" in q:
        return "Students should complete all prerequisites before registering for advanced CS courses."

    if "elective" in q:
        return "Students should choose approved COSC electives that satisfy their curriculum requirements."

    if "graduate" in q or "graduation" in q:
        return "To graduate, students must complete all required courses, electives, credits, and university requirements."

    if "credit" in q:
        return "A full-time student usually takes around 12 to 15 credits per semester."

    return "I can help with prerequisites, electives, graduation requirements, credits, and registration planning."


def run_advisor_agents(student_id, question):
    q = question.lower()

    if "next semester" in q or "take next" in q or "register" in q or "schedule" in q:
        return registration_planner_agent(student_id)

    if "progress" in q or "completed" in q or "taken" in q:
        return student_progress_agent(student_id)

    if "curriculum" in q or "required" in q or "classes do i need" in q:
        return curriculum_agent(question)

    if "prerequisite" in q or "elective" in q or "graduate" in q or "credit" in q:
        return policy_agent(question)

    return (
        "I can help with academic advising.\n\n"
        + registration_planner_agent(student_id)
    )