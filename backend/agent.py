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


def curriculum_agent():
    rows = query_db("""
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
        ORDER BY s.semester_number, cc.curriculum_id
    """)

    if not rows:
        return "No curriculum data was found."

    reply = "Computer Science Curriculum Plan:\n\n"
    current_term = ""

    for row in rows:
        term = f"{row['year_label']} - {row['term_label']}"

        if term != current_term:
            current_term = term
            reply += f"\n{term}\n"

        if row["course_code"]:
            reply += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            reply += f"- {row['placeholder_label']}"
            if row["choice_group"]:
                reply += f" Group {row['choice_group']}"
            reply += "\n"

    return reply


def semester_agent(question):
    q = question.lower()
    semester_number = None

    if "first semester" in q or "freshman" in q:
        semester_number = 1
    elif "second semester" in q:
        semester_number = 2
    elif "third semester" in q or "sophomore" in q:
        semester_number = 3
    elif "fourth semester" in q:
        semester_number = 4
    elif "fifth semester" in q or "junior" in q:
        semester_number = 5
    elif "sixth semester" in q:
        semester_number = 6
    elif "seventh semester" in q or "senior" in q:
        semester_number = 7
    elif "eighth semester" in q:
        semester_number = 8

    if semester_number is None:
        semester_number = 1

    rows = query_db("""
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

    if not rows:
        return "I could not find courses for that semester."

    reply = f"Recommended courses for {rows[0]['year_label']} {rows[0]['term_label']}:\n\n"

    for row in rows:
        if row["course_code"]:
            reply += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            reply += f"- {row['placeholder_label']}\n"

    return reply


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

    if group:
        rows = query_db("""
            SELECT course_code, course_title, credits
            FROM courses
            WHERE elective_group = ?
            ORDER BY course_code
        """, (group,))
    else:
        rows = query_db("""
            SELECT course_code, course_title, credits, elective_group
            FROM courses
            WHERE category = 'Elective'
            ORDER BY elective_group, course_code
        """)

    if not rows:
        return "I could not find elective courses."

    reply = "Available electives:\n\n"

    for row in rows:
        if "elective_group" in row:
            reply += f"- Group {row['elective_group']}: {row['course_code']} - {row['course_title']} ({row['credits']} credits)\n"
        else:
            reply += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"

    return reply


def graduation_requirements_agent():
    rows = query_db("""
        SELECT requirement_name, required_credits, required_gpa, description
        FROM graduation_requirements
        ORDER BY requirement_id
    """)

    if not rows:
        return "I could not find graduation requirements in the database."

    reply = "B.S. in Computer Science Graduation Requirements:\n\n"

    for row in rows:
        reply += f"- {row['requirement_name']}: "

        if row["required_credits"]:
            reply += f"{row['required_credits']} credits. "

        if row["required_gpa"]:
            reply += f"Minimum GPA: {row['required_gpa']}+. "

        reply += f"{row['description']}\n"

    return reply


def math_requirements_agent():
    rows = query_db("""
        SELECT course_code, course_title, credits
        FROM courses
        WHERE course_code IN ('MATH 241', 'MATH 242', 'MATH 312', 'MATH 331')
        ORDER BY course_code
    """)

    if not rows:
        return "I could not find the math requirements in the database."

    reply = "Math Requirements for the B.S. in Computer Science:\n\n"

    for row in rows:
        reply += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"

    reply += "\nThese math courses are part of the supporting course requirements."

    return reply


def career_paths_agent():
    rows = query_db("""
        SELECT job_title, description
        FROM career_paths
        ORDER BY job_title
    """)

    if not rows:
        return "I could not find career path information in the database."

    reply = "Jobs you can get with a B.S. in Computer Science:\n\n"

    for row in rows:
        reply += f"- {row['job_title']}: {row['description']}\n"

    return reply


def career_course_agent(question):
    q = question.lower()
    keyword = None

    if "software" in q or "developer" in q or "engineer" in q:
        keyword = "software"
    elif "cyber" in q or "security" in q:
        keyword = "cybersecurity"
    elif "data" in q or "analyst" in q or "scientist" in q:
        keyword = "data"
    elif "ai" in q or "machine learning" in q or "ml" in q:
        keyword = "ai"
    elif "web" in q or "full-stack" in q or "full stack" in q:
        keyword = "web"
    elif "devops" in q:
        keyword = "devops"
    elif "database" in q:
        keyword = "database"
    elif "qa" in q or "quality assurance" in q or "testing" in q:
        keyword = "qa"
    elif "network" in q:
        keyword = "network"
    elif "forensic" in q:
        keyword = "forensic"

    if keyword is None:
        return (
            "Tell me which career you are interested in, such as software engineer, "
            "cybersecurity analyst, data scientist, AI/ML engineer, web developer, "
            "DevOps engineer, database administrator, QA analyst, network architect, "
            "or forensic computer analyst."
        )

    rows = query_db("""
        SELECT 
            r.career_title,
            r.course_code,
            c.course_title,
            c.credits,
            r.reason
        FROM career_course_recommendations r
        LEFT JOIN courses c ON r.course_code = c.course_code
        WHERE r.career_keyword = ?
        ORDER BY r.recommendation_id
    """, (keyword,))

    if not rows:
        return "I could not find course recommendations for that career."

    career_title = rows[0]["career_title"]

    reply = f"If you are interested in becoming a {career_title}, consider these classes:\n\n"

    for row in rows:
        course_title = row["course_title"] or "Course not found in database"
        credits = row["credits"] or "N/A"

        reply += f"- {row['course_code']}: {course_title} ({credits} credits)\n"
        reply += f"  Reason: {row['reason']}\n"

    return reply


def run_advisor_agents(student_id, question):
    q = question.lower()

    if (
        "what classes should i take for" in q
        or "classes should i take for" in q
        or "interested in" in q
        or "want to be" in q
        or "career path" in q
        or "software engineer" in q
        or "software developer" in q
        or "cybersecurity analyst" in q
        or "data scientist" in q
        or "data analyst" in q
        or "machine learning" in q
        or "ai engineer" in q
        or "web developer" in q
        or "full stack" in q
        or "devops" in q
        or "database administrator" in q
        or "qa analyst" in q
        or "network architect" in q
        or "forensic" in q
    ):
        return career_course_agent(question)

    if "job" in q or "career" in q or "profession" in q or "what can i do with" in q:
        return career_paths_agent()

    if (
        "graduate" in q
        or "graduation" in q
        or "degree requirements" in q
        or "b.s" in q
        or "bs degree" in q
        or "120 credits" in q
        or "gpa" in q
    ):
        return graduation_requirements_agent()

    if "math" in q or "calculus" in q or "linear algebra" in q or "statistics" in q:
        return math_requirements_agent()

    if "elective" in q or "group a" in q or "group b" in q or "group c" in q or "group d" in q:
        return elective_agent(question)

    if (
        "first semester" in q
        or "freshman" in q
        or "second semester" in q
        or "third semester" in q
        or "sophomore" in q
        or "fourth semester" in q
        or "junior" in q
        or "senior" in q
        or "semester" in q
        or "next semester" in q
        or "take next" in q
        or "register" in q
    ):
        return semester_agent(question)

    if "curriculum" in q or "required" in q or "classes do i need" in q or "course plan" in q:
        return curriculum_agent()

    return (
        "I can help with your Computer Science advising plan.\n\n"
        "Try asking:\n"
        "- What classes should I take first semester?\n"
        "- What electives are in Group A?\n"
        "- Show me the full curriculum.\n"
        "- What are the graduation requirements?\n"
        "- What math classes do I need?\n"
        "- What jobs can I get with a computer science degree?\n"
        "- What classes should I take if I want to be a software engineer?\n"
        "- What classes should I take for cybersecurity?"
    )