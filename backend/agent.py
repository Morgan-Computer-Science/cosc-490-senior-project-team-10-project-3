# backend/agent.py

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_advisor.db")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None

try:
    if GEMINI_API_KEY:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print("Gemini setup failed:", e)
    client = None

def small_talk_agent(question):
    q = question.lower().strip()

    if q in ["hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"]:
        return """
Hi! I’m MSU CS Scholar, your Morgan State Computer Science advising assistant.

I can help with:
- Choosing classes
- Understanding the CS curriculum
- Electives
- Graduation requirements
- Math requirements
- Career paths
- Faculty information
- Registration, WebSIS, Canvas, tuition, overrides, and appeals
"""

    if (
        "what do you do" in q
        or "what can you do" in q
        or "who are you" in q
        or "help me" in q
    ):
        return """
I’m MSU CS Scholar. I help Morgan State Computer Science students with academic advising.

You can ask me things like:
- What classes should I take first semester?
- What electives are in Group A?
- Who are the Computer Science faculty?
- How do I request an override?
- How do I request an appeal?
- What jobs can I get with a Computer Science degree?
"""

    return ""

def faculty_agent():
    return """
Morgan State University Computer Science Faculty:

- Dr. Hong Wang – Department Chair / Faculty
- Dr. Nilanjan Banerjee – Computer Science Faculty
- Dr. Shiv Sharma – Computer Science Faculty
- Dr. Danda Rawat – Computer Science Faculty
- Dr. Fisseha Mekuria – Computer Science Faculty
- Dr. Youakim Badr – Computer Science Faculty

For the latest office hours, advising, and research areas, visit the Morgan State University Computer Science Department website.
"""

def query_db(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print("Database error:", e)
        return []


def ask_gemini(question, context=""):
    if not client:
        if context:
            return context
        return (
            "I can help with Computer Science advising, but Gemini is not connected yet. "
            "Make sure GEMINI_API_KEY is saved correctly in your backend/.env file."
        )

    prompt = f"""
You are MSU CS Scholar, a Computer Science academic advising assistant for Morgan State University students.

Your job:
- Help students choose classes.
- Explain curriculum requirements.
- Recommend electives.
- Help with career-based course planning.
- Explain graduation requirements.
- Tell students that override requests should be sent to Dr. Wang and the academic advisors.
- Do not make up requirements.
- Use the database context when available.

Student question:
{question}

Database context:
{context}

Give a clear, friendly advising answer.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        if context:
            return context
        return "The AI model had an error, but the advising system is still running."


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
        return "No curriculum data was found in the database."

    context = "Computer Science Curriculum Plan:\n\n"
    current_term = ""

    for row in rows:
        term = f"{row['year_label']} - {row['term_label']}"

        if term != current_term:
            current_term = term
            context += f"\n{term}\n"

        if row["course_code"]:
            context += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            context += f"- {row['placeholder_label']}"
            if row["choice_group"]:
                context += f" Group {row['choice_group']}"
            context += "\n"

    return context


def semester_agent(question):
    q = question.lower()

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
    else:
        semester_number = 1

    rows = query_db("""
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

    if not rows:
        return "I could not find courses for that semester."

    context = f"Recommended courses for {rows[0]['year_label']} {rows[0]['term_label']}:\n\n"

    for row in rows:
        if row["course_code"]:
            context += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"
        else:
            context += f"- {row['placeholder_label']}\n"

    return context



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
            WHERE elective_group IS NOT NULL
            ORDER BY elective_group, course_code
        """)

    if not rows:
        return "I could not find elective courses."

    context = "Available electives:\n\n"

    for row in rows:
        if "elective_group" in row:
            context += f"- Group {row['elective_group']}: {row['course_code']} - {row['course_title']} ({row['credits']} credits)\n"
        else:
            context += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"

    return context


def graduation_requirements_agent():
    rows = query_db("""
        SELECT requirement_name, required_credits, required_gpa, description
        FROM graduation_requirements
        ORDER BY requirement_id
    """)

    if not rows:
        return "I could not find graduation requirements in the database."

    context = "B.S. in Computer Science Graduation Requirements:\n\n"

    for row in rows:
        context += f"- {row['requirement_name']}: "

        if row["required_credits"]:
            context += f"{row['required_credits']} credits. "

        if row["required_gpa"]:
            context += f"Minimum GPA: {row['required_gpa']}+. "

        context += f"{row['description']}\n"

    return context


def math_requirements_agent():
    rows = query_db("""
        SELECT course_code, course_title, credits
        FROM courses
        WHERE course_code LIKE 'MATH%'
        ORDER BY course_code
    """)

    if not rows:
        return "I could not find math requirements in the database."

    context = "Math Requirements for Computer Science:\n\n"

    for row in rows:
        context += f"- {row['course_code']}: {row['course_title']} ({row['credits']} credits)\n"

    return context

def appeal_agent():
    return """
Academic Appeal Guidance:

If you need to request an appeal at Morgan State University, start by contacting your academic advisor or the appropriate department office.

Common appeals may include:
- Academic standing appeals
- Registration issues
- Prerequisite overrides
- Late withdrawal requests
- Graduation requirement concerns
- Grade disputes (follow official procedures)

Recommended steps:
1. Speak with your academic advisor first.
2. Explain your situation clearly.
3. Gather supporting documents.
4. Complete any required university forms.
5. Submit before deadlines.

For Computer Science matters, contact Dr. Wang and your assigned advisor.
"""

def career_paths_agent():
    rows = query_db("""
        SELECT job_title, description
        FROM career_paths
        ORDER BY job_title
    """)

    if not rows:
        return (
            "Computer Science students can prepare for careers like software engineer, "
            "cybersecurity analyst, data analyst, web developer, AI/ML engineer, database administrator, "
            "network engineer, and QA analyst."
        )

    context = "Jobs you can get with a B.S. in Computer Science:\n\n"

    for row in rows:
        context += f"- {row['job_title']}: {row['description']}\n"

    return context


def career_course_agent(question):
    q = question.lower()
    keyword = None

    if "software" in q or "developer" in q or "engineer" in q:
        keyword = "software"
    elif "cyber" in q or "security" in q:
        keyword = "cybersecurity"
    elif "data" in q:
        keyword = "data"
    elif "ai" in q or "machine learning" in q or "ml" in q:
        keyword = "ai"
    elif "web" in q or "full stack" in q or "full-stack" in q:
        keyword = "web"
    elif "devops" in q:
        keyword = "devops"
    elif "database" in q:
        keyword = "database"
    elif "qa" in q or "testing" in q:
        keyword = "qa"
    elif "network" in q:
        keyword = "network"
    elif "forensic" in q:
        keyword = "forensic"

    if keyword is None:
        return ""

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
        return f"I could not find course recommendations for {keyword} in the database."

    context = f"Course recommendations for becoming a {rows[0]['career_title']}:\n\n"

    for row in rows:
        course_title = row["course_title"] or "Course not found in database"
        credits = row["credits"] or "N/A"
        context += f"- {row['course_code']}: {course_title} ({credits} credits)\n"
        context += f"  Reason: {row['reason']}\n"

    return context


def student_gateway_agent():
    return """
Student Gateway Help:

You can use Morgan State University's student systems for registration, tuition, Canvas, WebSIS, and personal information updates.

Common guidance:
- Register for classes through WebSIS / Student Self-Service.
- Pay tuition through the student account/payment portal.
- Use Canvas for course materials.
- Use the academic calendar to check registration, add/drop, and payment deadlines.
- For course overrides, contact Dr. Wang and your academic advisor.
"""


def override_agent():
    return """
Course Override Guidance:

If you need an override for a Computer Science course, contact Dr. Wang and your academic advisor.

Include:
- Your full name
- Student ID
- Course name and section
- Reason for the override
- Any prerequisite or scheduling issue
"""


def get_agent_context(question):
    q = question.lower()
    
    small_talk_response = small_talk_agent(question)
    if small_talk_response:
        return small_talk_response
    
    if (
        "appeal" in q
        or "request an appeal" in q
        or "academic appeal" in q
    ):
        return appeal_agent()
    
    if (
        "faculty" in q
        or "professor" in q
        or "professors" in q
        or "teacher" in q
        or "teachers" in q
        or "staff" in q
        or "department chair" in q
        or "chair" in q
        or "who teaches" in q
        or "computer science faculty" in q
        or "cs faculty" in q
    ):
        return faculty_agent()
    if "override" in q or "permission" in q:
        return override_agent()

    if (
        "where can i register" in q
        or "register my classes" in q
        or "registration" in q
        or "student gateway" in q
        or "websis" in q
        or "tuition" in q
        or "pay" in q
        or "canvas" in q
        or "academic calendar" in q
        or "personal information" in q
    ):
        return student_gateway_agent()

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
    ):
        return semester_agent(question)

    if "curriculum" in q or "required" in q or "classes do i need" in q or "course plan" in q:
        return curriculum_agent()

    return ""


def run_advisor_agents(student_id, question):
    context = get_agent_context(question)

    if not context:
        context = """ recommend contacting Morgan State Computer Science advisors.
"""

    return ask_gemini(question, context)