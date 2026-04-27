import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def curriculum_agent(question):
    q = question.lower()

    semester_map = {
        "freshman first": 1,
        "first semester freshman": 1,
        "freshman second": 2,
        "second semester freshman": 2,
        "sophomore first": 3,
        "third semester": 3,
        "sophomore second": 4,
        "fourth semester": 4,
        "junior first": 5,
        "fifth semester": 5,
        "junior second": 6,
        "sixth semester": 6,
        "senior first": 7,
        "seventh semester": 7,
        "senior second": 8,
        "eighth semester": 8,
    }

    semester_number = None

    for phrase, number in semester_map.items():
        if phrase in q:
            semester_number = number
            break

    if semester_number is None:
        if "freshman" in q:
            semester_number = 1
        elif "sophomore" in q:
            semester_number = 3
        elif "junior" in q:
            semester_number = 5
        elif "senior" in q:
            semester_number = 7

    if semester_number is None:
        return None

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.year_label,
            s.term_label,
            c.course_code,
            c.course_title,
            c.credits,
            cc.placeholder_label
        FROM curriculum_courses cc
        JOIN semesters s ON cc.semester_id = s.semester_id
        LEFT JOIN courses c ON cc.course_id = c.course_id
        WHERE s.semester_number = ?
        ORDER BY cc.curriculum_id
    """, (semester_number,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    answer = f"For {rows[0]['year_label']} {rows[0]['term_label']}, you should take:\n\n"

    for row in rows:
        if row["course_code"]:
            answer += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            answer += f"- {row['placeholder_label']}\n"

    return answer


def course_agent(question):
    q = question.lower()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT course_code, course_title, credits, category, elective_group
        FROM courses
        WHERE lower(course_code) LIKE ?
           OR lower(course_title) LIKE ?
        ORDER BY course_code
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    answer = "I found this course information in the database:\n\n"

    for row in rows:
        group_text = f", Group {row['elective_group']}" if row["elective_group"] else ""
        answer += (
            f"- {row['course_code']}: {row['course_title']} "
            f"({row['credits']} credits, {row['category']}{group_text})\n"
        )

    return answer


def elective_agent(question):
    q = question.lower()

    group = None
    if "group a" in q:
        group = "A"
    elif "group b" in q:
        group = "B"
    elif "group c" in q:
        group = "C"
    elif "group d" in q:
        group = "D"
    elif "elective" not in q:
        return None

    conn = get_db()
    cur = conn.cursor()

    if group:
        cur.execute("""
            SELECT course_code, course_title, credits
            FROM courses
            WHERE elective_group = ?
            ORDER BY course_code
        """, (group,))
    else:
        cur.execute("""
            SELECT course_code, course_title, credits, elective_group
            FROM courses
            WHERE category = 'Elective'
            ORDER BY elective_group, course_code
        """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    if group:
        answer = f"Here are the Group {group} electives:\n\n"
    else:
        answer = "Here are the electives in the database:\n\n"

    for row in rows:
        answer += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"

    return answer


def graduation_agent(question):
    q = question.lower()

    if "graduation" not in q and "graduate" not in q and "requirements" not in q:
        return None

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.course_code,
            c.course_title,
            c.credits,
            cc.placeholder_label
        FROM curriculum_courses cc
        LEFT JOIN courses c ON cc.course_id = c.course_id
        ORDER BY cc.semester_id, cc.curriculum_id
    """)

    rows = cur.fetchall()
    conn.close()

    answer = "The Computer Science graduation plan includes these curriculum requirements:\n\n"

    for row in rows:
        if row["course_code"]:
            answer += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            answer += f"- {row['placeholder_label']}\n"

    return answer


def general_agent(question):
    return (
        "I can answer questions using the MSU CS Scholar database. Try asking:\n\n"
        "- What classes should I take freshman first semester?\n"
        "- What should I take junior year?\n"
        "- Show me Group A electives\n"
        "- What is COSC 354?\n"
        "- What are the graduation requirements?"
    )


def run_advisor_agents(question):
    agents = [
        curriculum_agent,
        elective_agent,
        course_agent,
        graduation_agent,
        general_agent
    ]

    for agent in agents:
        answer = agent(question)
        if answer:
            return answer

    return general_agent(question)