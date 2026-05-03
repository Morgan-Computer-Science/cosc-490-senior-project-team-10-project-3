import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")

def detect_semester_number(q):
    if "3rd semester" in q or "third semester" in q or "semester 3" in q:
        return 3
    if "4th semester" in q or "fourth semester" in q:
        return 4
    if "5th semester" in q or "fifth semester" in q:
        return 5
    if "6th semester" in q or "sixth semester" in q:
        return 6
    if "7th semester" in q or "seventh semester" in q:
        return 7
    if "8th semester" in q or "eighth semester" in q:
        return 8
    if "2nd semester" in q or "second semester" in q:
        return 2
    return 1

def get_db_answer(question):
    q = question.lower().strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        semester_number = detect_semester_number(q)

        if (
            "freshman" in q
            or "first year" in q
            or "1st year" in q
            or "semester" in q
            or "what classes should i take" in q
            or "courses should i take" in q
        ):

            rows = cursor.execute("""
                SELECT
                    s.year_label,
                    s.term_label,
                    c.course_code,
                    c.course_title,
                    c.credits,
                    cc.placeholder_label,
                    cc.requirement_type
                FROM curriculum_courses cc
                JOIN semesters s ON cc.semester_id = s.semester_id
                LEFT JOIN courses c ON cc.course_id = c.course_id
                WHERE s.semester_number = ?
                ORDER BY cc.curriculum_id
            """, (semester_number,)).fetchall()

            if not rows:
                return None

            title = f"{rows[0]['year_label']} {rows[0]['term_label']} recommended courses:"
            lines = [title]

            for row in rows:
                if row["course_code"]:
                    lines.append(
                        f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)"
                    )
                else:
                    lines.append(
                        f"- {row['placeholder_label']} ({row['requirement_type']})"
                    )

            return "\n".join(lines)

        if "graduation" in q or "graduate" in q or "requirements" in q:
            rows = cursor.execute("""
                SELECT requirement_name, description
                FROM graduation_requirements
            """).fetchall()

            return "Graduation requirements:\n" + "\n".join(
                f"- {row['requirement_name']}: {row['description']}"
                for row in rows
            )

        if "math" in q:
            rows = cursor.execute("""
                SELECT course_code, course_title, credits
                FROM courses
                WHERE course_code LIKE 'MATH%'
                ORDER BY course_code
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