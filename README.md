# Multimodal AI Student Advisor

The Multimodal AI Student Advisor is an intelligent academic advising system designed to help university students with course planning, degree progress, career guidance, and campus support.

The system uses a multimodal AI and agent-based architecture to understand student questions, uploaded documents, and academic data. It can assist with text-based advising, transcript or resume review, curriculum planning, and guidance through academic workflows.

## Features

- Academic advising chatbot
- Degree and curriculum planning
- Course recommendations based on career goals
- Resume and Degree Works document support
- Morgan State University Computer Science advising information
- RAG-based responses using academic data
- Guidance for registration, tuition, Canvas, WebSIS, and academic calendar links
- Support for appeals, overrides, faculty information, and on-campus resources
- Future support for multimodal vision, language, and action capabilities

## Technologies Used

- Python
- Flask
- Flask-CORS
- SQLite
- Google Gemini / Vertex AI
- HTML, CSS, JavaScript
- Tailwind CSS

## Project Structure

```text
backend/
  app.py
  agent.py
  class_database.py
  student_advisor.db
  requirements.txt
  .env

frontend/
  chat_dashboard/
  login/
  signup_onboarding/

#Setup Instructions
Step 1: Open the project
cd /workspaces/cosc-490-senior-project-team-10-project-3
Step 2: Go into the backend folder
cd backend
Step 3: Install dependencies
pip install flask flask-cors
pip install -r requirements.txt
Step 4: Create the environment file
Create a file named .env inside the backend/ folder.
Step 5: Run the Flask backend
python3 app.py
Step 6: Open the app
Go to the Ports tab in Codespaces and open the link for port 5000.

