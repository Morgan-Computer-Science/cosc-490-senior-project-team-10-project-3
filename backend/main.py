def advisor_agent(student, question):
    if "classes" in question.lower():
        return f"{student['name']}, based on your GPA ({student['gpa']}), you should take:\n- COSC202 (Data Structures)\n- MATH241 (Calculus II)"
    
    elif "gpa" in question.lower():
        return f"Your current GPA is {student['gpa']}. You're doing well, keep it up!"
    
    return "I recommend meeting with your advisor for more guidance."


def run_demo():
    print("🎓 AI Student Advisor Demo\n")

    student = {
        "name": "John Doe",
        "year": "Sophomore",
        "completed_courses": ["COSC111", "MATH141"],
        "gpa": 3.2
    }

    question = input("Ask the advisor: ")

    response = advisor_agent(student, question)

    print("\n🤖 Advisor Response:")
    print(response)


if __name__ == "__main__":
    run_demo()

