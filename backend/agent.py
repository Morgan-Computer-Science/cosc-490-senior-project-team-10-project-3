import asyncio
import traceback
from database_tools import get_db_answer

try:
    from google_cloud_agent import app as cloud_agent
except Exception as e:
    print("Could not import google_cloud_agent:", e)
    traceback.print_exc()
    cloud_agent = None


if cloud_agent:
    try:
        cloud_agent.set_up()
        print("Google Cloud Agent loaded successfully.")
    except Exception as e:
        print("Google Cloud Agent setup failed:", e)
        traceback.print_exc()
        cloud_agent = None


async def ask_google_cloud_agent(question, student_id=1):
    final_text = ""

    async for chunk in cloud_agent.stream_query(
        message=question,
        session_id=f"student-{student_id}",
        user_id=str(student_id),
    ):
        if isinstance(chunk, dict):
            content = chunk.get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                if isinstance(part, dict):
                    final_text += part.get("text", "")
        else:
            text = getattr(chunk, "text", "")
            if text:
                final_text += text

    return final_text.strip()


def run_advisor_agents(student_id, question):
    db_answer = get_db_answer(question)
    if db_answer:
        return db_answer

    if not question or not question.strip():
        return "Please ask a question first."

    if not cloud_agent:
        return (
            "The Google Cloud AI agent is not connected yet. "
            "Make sure google_cloud_agent.py is in the backend folder and your Google Cloud setup is correct."
        )

    try:
        response = asyncio.run(ask_google_cloud_agent(question, student_id))
        return response or "I could not generate a response from the Google Cloud agent."

    except Exception as e:
        print("Google Cloud Agent error:", e)
        traceback.print_exc()
        return f"Google Cloud Agent error: {type(e).__name__}: {e}"
   