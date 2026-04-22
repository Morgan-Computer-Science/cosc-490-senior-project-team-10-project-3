import sqlite3

conn = sqlite3.connect("student_advisor.db")
cursor = conn.cursor()

print("Semester 3 plan:")
rows = cursor.execute("""
SELECT
    s.year_label,
    s.term_label,
    COALESCE(c.course_code, '[' || cc.placeholder_label || ']') AS item,
    COALESCE(c.course_title, cc.placeholder_label) AS title,
    cc.requirement_type
FROM curriculum_courses cc
JOIN semesters s ON s.semester_id = cc.semester_id
LEFT JOIN courses c ON c.course_id = cc.course_id
WHERE cc.semester_id = 3
""").fetchall()

for row in rows:
    print(row)

print("\nGroup A elective choices:")
rows = cursor.execute("""
SELECT course_code, course_title, credits
FROM courses
WHERE elective_group = 'A'
ORDER BY course_code
""").fetchall()

for row in rows:
    print(row)

conn.close()