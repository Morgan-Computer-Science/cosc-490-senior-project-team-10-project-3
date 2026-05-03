import sqlite3

conn = sqlite3.connect("student_advisor.db")
cursor = conn.cursor()

cursor.executescript("""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    class_level TEXT NOT NULL,
    current_semester INTEGER NOT NULL,
    credits_earned INTEGER NOT NULL,
    status_note TEXT
);

CREATE TABLE IF NOT EXISTS student_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    completed_course_code TEXT NOT NULL,
    completed_course_title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    term_completed TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
""")

students = [
    ("Aaliyah", "Brooks", "Freshman", 1, 12, "Just started first year"),
    ("Jordan", "Carter", "Freshman", 1, 9, "Needs one gen ed to stay on track"),
    ("Malik", "Evans", "Freshman", 2, 15, "Completed first semester"),
    ("Nia", "Foster", "Freshman", 2, 14, "Taking second semester now"),
    ("Xavier", "Green", "Freshman", 2, 16, "Ahead by one course"),

    ("Amara", "Hughes", "Sophomore", 3, 30, "Started sophomore sequence"),
    ("Jaylen", "Ingram", "Sophomore", 3, 29, "Needs Group A elective"),
    ("Kayla", "Johnson", "Sophomore", 4, 45, "On track through fourth semester"),
    ("Elijah", "King", "Sophomore", 4, 43, "Missing one AH general education course"),
    ("Destiny", "Lewis", "Sophomore", 4, 47, "Completed two Group A electives"),

    ("Noah", "Mitchell", "Junior", 5, 58, "Beginning junior core"),
    ("Brianna", "Nelson", "Junior", 5, 60, "On track with fifth semester"),
    ("Isaiah", "Owens", "Junior", 6, 72, "Completed one Group B elective"),
    ("Jasmine", "Parker", "Junior", 6, 74, "Needs CI requirement"),
    ("Camden", "Roberts", "Junior", 6, 76, "Finished junior core except one elective"),

    ("Zaria", "Scott", "Senior", 7, 88, "Starting senior year"),
    ("Micah", "Turner", "Senior", 7, 90, "Taking Software Engineering and Database Design"),
    ("Sydney", "Walker", "Senior", 8, 104, "Needs one Group C elective"),
    ("Darius", "Young", "Senior", 8, 108, "Needs Group D elective and SB requirement"),
    ("Imani", "Bennett", "Senior", 8, 112, "Almost done, taking Senior Project")
]

cursor.executemany("""
INSERT INTO students (first_name, last_name, class_level, current_semester, credits_earned, status_note)
VALUES (?, ?, ?, ?, ?, ?)
""", students)

progress = [
    # Freshmen
    (1, "ENGL 101", "Composition I", 3, "Fall 2025"),
    (1, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2025"),
    (1, "MATH 241", "Calculus I", 4, "Fall 2025"),

    (2, "ENGL 101", "Composition I", 3, "Fall 2025"),
    (2, "ORNS 106", "Freshman Orientation", 1, "Fall 2025"),

    (3, "ENGL 101", "Composition I", 3, "Fall 2025"),
    (3, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2025"),
    (3, "MATH 241", "Calculus I", 4, "Fall 2025"),
    (3, "ORNS 106", "Freshman Orientation", 1, "Fall 2025"),

    (4, "ENGL 101", "Composition I", 3, "Fall 2025"),
    (4, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2025"),
    (4, "MATH 241", "Calculus I", 4, "Fall 2025"),

    (5, "ENGL 101", "Composition I", 3, "Fall 2025"),
    (5, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2025"),
    (5, "MATH 241", "Calculus I", 4, "Fall 2025"),
    (5, "ENGL 102", "Composition II", 3, "Spring 2026"),
    (5, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2026"),

    # Sophomores
    (6, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2024"),
    (6, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2025"),
    (6, "MATH 241", "Calculus I", 4, "Fall 2024"),
    (6, "MATH 242", "Calculus II", 4, "Spring 2025"),

    (7, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2024"),
    (7, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2025"),
    (7, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2025"),
    (7, "COSC 241", "Computer Systems and Digital Logic", 3, "Fall 2025"),

    (8, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2024"),
    (8, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2025"),
    (8, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2025"),
    (8, "COSC 241", "Computer Systems and Digital Logic", 3, "Fall 2025"),
    (8, "COSC 281", "Discrete Structure", 3, "Spring 2026"),
    (8, "MATH 312", "Linear Algebra I", 3, "Spring 2026"),

    (9, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2024"),
    (9, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2025"),
    (9, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2025"),
    (9, "COSC 201", "Computer Ethics", 1, "Fall 2025"),

    (10, "COSC 111", "Introduction to Computer Science I", 4, "Fall 2024"),
    (10, "COSC 112", "Introduction to Computer Science II", 4, "Spring 2025"),
    (10, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2025"),
    (10, "COSC 241", "Computer Systems and Digital Logic", 3, "Fall 2025"),
    (10, "COSC 281", "Discrete Structure", 3, "Spring 2026"),
    (10, "COSC 239", "Java Programming", 3, "Spring 2026"),
    (10, "COSC 251", "Introduction to Data Science", 3, "Spring 2026"),

    # Juniors
    (11, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2024"),
    (11, "COSC 241", "Computer Systems and Digital Logic", 3, "Fall 2024"),
    (11, "COSC 281", "Discrete Structure", 3, "Spring 2025"),

    (12, "COSC 220", "Data Structures and Algorithms", 4, "Fall 2024"),
    (12, "COSC 241", "Computer Systems and Digital Logic", 3, "Fall 2024"),
    (12, "COSC 281", "Discrete Structure", 3, "Spring 2025"),
    (12, "COSC 349", "Computer Networks", 3, "Fall 2025"),
    (12, "COSC 351", "Cybersecurity", 3, "Fall 2025"),

    (13, "COSC 349", "Computer Networks", 3, "Fall 2025"),
    (13, "COSC 351", "Cybersecurity", 3, "Fall 2025"),
    (13, "COSC 352", "Organization of Programming Languages", 3, "Fall 2025"),
    (13, "COSC 323", "Introduction to Cryptography", 3, "Spring 2026"),

    (14, "COSC 349", "Computer Networks", 3, "Fall 2025"),
    (14, "COSC 351", "Cybersecurity", 3, "Fall 2025"),
    (14, "COSC 352", "Organization of Programming Languages", 3, "Fall 2025"),
    (14, "COSC 354", "Operating Systems", 3, "Spring 2026"),

    (15, "COSC 349", "Computer Networks", 3, "Fall 2025"),
    (15, "COSC 351", "Cybersecurity", 3, "Fall 2025"),
    (15, "COSC 352", "Organization of Programming Languages", 3, "Fall 2025"),
    (15, "COSC 354", "Operating Systems", 3, "Spring 2026"),
    (15, "MATH 331", "Applied Probability and Statistics", 3, "Spring 2026"),
    (15, "COSC 320", "Algorithm Design and Analysis", 3, "Spring 2026"),

    # Seniors
    (16, "COSC 354", "Operating Systems", 3, "Spring 2025"),
    (16, "MATH 331", "Applied Probability and Statistics", 3, "Spring 2025"),

    (17, "COSC 354", "Operating Systems", 3, "Spring 2025"),
    (17, "MATH 331", "Applied Probability and Statistics", 3, "Spring 2025"),
    (17, "COSC 458", "Software Engineering", 3, "Fall 2025"),

    (18, "COSC 458", "Software Engineering", 3, "Fall 2025"),
    (18, "COSC 459", "Database Design", 3, "Fall 2025"),
    (18, "COSC 470", "Artificial Intelligence", 3, "Fall 2025"),
    (18, "COSC 460", "Computer Graphics", 3, "Spring 2026"),

    (19, "COSC 458", "Software Engineering", 3, "Fall 2025"),
    (19, "COSC 459", "Database Design", 3, "Fall 2025"),
    (19, "COSC 490", "Senior Project", 3, "Spring 2026"),

    (20, "COSC 458", "Software Engineering", 3, "Fall 2025"),
    (20, "COSC 459", "Database Design", 3, "Fall 2025"),
    (20, "COSC 490", "Senior Project", 3, "Spring 2026"),
    (20, "COSC 472", "Introduction to Machine Learning", 3, "Spring 2026"),
]
cursor.executemany("""
INSERT INTO student_progress (student_id, completed_course_code, completed_course_title, credits, term_completed)
VALUES (?, ?, ?, ?, ?)
""", progress)

conn.commit()
conn.close()

print("Added 20 fictional students and their curriculum progress.")

import sqlite3

conn = sqlite3.connect("student_advisor.db")
cursor = conn.cursor()

rows = cursor.execute("""
SELECT first_name, last_name, class_level, current_semester, credits_earned, status_note
FROM students
ORDER BY current_semester, last_name
""").fetchall()

for row in rows:
    print(row)

conn.close()