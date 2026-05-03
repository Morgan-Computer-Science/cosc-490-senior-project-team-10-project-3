import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")


def get_db_answer(question):
    q = question.lower().strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        if "graduation" in q or "graduate" in q or "requirements" in q:
            rows = cursor.execute("""
                SELECT requirement_name, description
                FROM graduation_requirements
            """).fetchall()

            return "\n".join(
                f"{row['requirement_name']}: {row['description']}"
                for row in rows
            )

        if "math" in q:
            rows = cursor.execute("""
                SELECT course_code, course_title, credits
                FROM courses
                WHERE course_code LIKE 'MATH%'
            """).fetchall()

            return "Required math courses:\n" + "\n".join(
                f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)"
                for row in rows
            )

        if "elective" in q:
            rows = cursor.execute("""
                SELECT course_code, course_title, credits, elective_group
                FROM courses
                WHERE category = 'Elective'
                ORDER BY elective_group, course_code
            """).fetchall()

            return "Computer Science electives:\n" + "\n".join(
                f"- Group {row['elective_group']}: {row['course_code']} {row['course_title']} ({row['credits']} credits)"
                for row in rows
            )

        if "career" in q or "job" in q:
            rows = cursor.execute("""
                SELECT job_title, description
                FROM career_paths
            """).fetchall()

            return "Computer Science career paths:\n" + "\n".join(
                f"- {row['job_title']}: {row['description']}"
                for row in rows
            )

        return None

    finally:
        conn.close()