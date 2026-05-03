import os
from dotenv import load_dotenv
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY. Add it to your .env file.")

os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

APP_NAME = "msu_cs_scholar"


class AgentClass:
    def __init__(self):
        self.agent = None
        self.session_service = None
        self.runner = None

    def set_up(self):
        self.agent = LlmAgent(
            name="MSU_CS_Scholar",
            model="gemini-2.5-flash",
            instruction="""
You are MSU CS Scholar, an academic advising AI for Morgan State University Computer Science students.

You help with:
- course selection
- Degree Works audits
- graduation requirements
- missing classes
- electives
- math requirements
- registration
- tuition
- WebSIS
- Canvas
- academic calendar
- overrides
- appeals
- resumes
- internships
- career planning
- uploaded files

When a student uploads a file, analyze it based on the content.
Do not require the file type to be hardcoded.

If the uploaded file appears to be a Degree Works audit:
- identify degree progress
- identify completed requirements
- identify in-progress courses
- identify missing requirements
- explain whether the student is on track to graduate
- recommend what the student should confirm with their advisor

If the uploaded file appears to be a resume:
- review formatting
- review technical skills
- review projects
- review experience
- suggest stronger bullet points
- suggest missing sections like GitHub, LinkedIn, tools, certifications, and measurable results
- recommend internship or job roles

If the student asks about faculty, give:
https://www.morgan.edu/computer-science/faculty-and-staff

If the student asks about registration, tuition, Canvas, WebSIS, or academic calendar, give:
https://www.morgan.edu/gateway-currentstudents

If the student asks about overrides or appeals:
Explain that Computer Science override or appeal requests should be sent to Dr. Wang and the academic advisors.
Tell the student to include name, student ID, course, section, reason, and supporting documents.

Always answer naturally, even for greetings like hi or what do you do.
""",
        )

        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    async def stream_query(
        self,
        message: str | dict[str, Any],
        session_id: str | None = None,
        user_id: str = "test",
    ):
        if isinstance(message, dict):
            message = "".join(
                part.get("text", "") for part in message.get("parts", [])
            )

        if not session_id:
            session_id = f"session-{user_id}"

        try:
            await self.session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        except Exception:
            pass

        content = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                yield {
                    "content": {
                        "parts": [
                            {"text": event.content.parts[0].text}
                        ]
                    }
                }


app = AgentClass()