from flask import Flask, request, render_template_string
import openai
import os
import json
import time
import requests
import markdown
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

with open("assistant_id.json") as f:
    assistant_id = json.load(f)["assistant_id"]

GOOGLE_ACCESS_TOKEN = None
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def load_index_html():
    with open("index.html", "r") as f:
        return f.read()

def format_pretty_datetime(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        return dt.strftime("%A, %B %d, %Y at %I:%M %p")
    except Exception as e:
        print("Error formatting date:", e)
        return dt_string

def refresh_google_token():
    global GOOGLE_ACCESS_TOKEN
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": GOOGLE_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    res = requests.post(url, data=data)
    if res.status_code == 200:
        GOOGLE_ACCESS_TOKEN = res.json()["access_token"]
        print("Refreshed Google access token.")
        return True
    else:
        print("Failed to refresh token:", res.text)
        return False

def create_event_in_calendar(summary, start, end, tags):
    if not summary or not start or not end:
        return {
            "status": "error",
            "detail": "Missing summary, start, or end time. Cannot create event."
        }

    if not GOOGLE_ACCESS_TOKEN:
        refresh_google_token()

    headers = {
        "Authorization": f"Bearer {GOOGLE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    event_data = {
        "summary": summary,
        "start": {
            "dateTime": start if "T" in start else start + "T09:00:00",
            "timeZone": "America/Los_Angeles"
        },
        "end": {
            "dateTime": end if "T" in end else end + "T10:00:00",
            "timeZone": "America/Los_Angeles"
        },
        "description": ", ".join(tags) if tags else ""
    }

    res = requests.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers=headers,
        json=event_data
    )

    if res.status_code == 401:
        print("Access token expired. Refreshing...")
        if refresh_google_token():
            headers["Authorization"] = f"Bearer {GOOGLE_ACCESS_TOKEN}"
            res = requests.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers=headers,
                json=event_data
            )

    if res.status_code in [200, 201]:
        event = res.json()
        return {
            "status": "success",
            "summary": event.get("summary"),
            "start": event.get("start", {}).get("dateTime"),
            "end": event.get("end", {}).get("dateTime"),
            "link": event.get("htmlLink")
        }
    else:
        print("Failed to create event:", res.text)
        return {
            "status": "error",
            "detail": f"Google Calendar API error: {res.text}"
        }

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        user_input = request.form["event_text"]
        final_summary = None
        final_start = None
        final_link = None

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            system_message = f"Today is {today}."
            final_user_input = f"{system_message}\n\n{user_input}"

            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=final_user_input
            )
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )

            start_time = time.time()
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "requires_action":
                    tool_outputs = []
                    for call in run_status.required_action.submit_tool_outputs.tool_calls:
                        if call.function.name == "create_calendar_event":
                            args = json.loads(call.function.arguments)
                            result_calendar = create_event_in_calendar(
                                args.get("summary"),
                                args.get("start"),
                                args.get("end"),
                                args.get("tags", [])
                            )

                            if result_calendar.get("status") == "success":
                                final_summary = result_calendar.get("summary")
                                final_start = result_calendar.get("start")
                                final_link = result_calendar.get("link")

                            tool_outputs.append({
                                "tool_call_id": call.id,
                                "output": json.dumps(result_calendar)
                            })

                    if tool_outputs:
                        openai.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )

                elif run_status.status == "completed":
                    break
                elif time.time() - start_time > 60:
                    result = "Assistant timed out."
                    break
                time.sleep(0.5)

            if not result:
                if final_summary and final_start:
                    pretty_start = format_pretty_datetime(final_start)
                    result = f"""
                    <div>
                        <strong>Successfully scheduled!</strong><br>
                        <strong>Title:</strong> {final_summary}<br>
                        <strong>Start time:</strong> {pretty_start}<br>
                        <a href="{final_link}" target="_blank">View on Google Calendar</a>
                    </div>
                    """
                else:
                    messages = openai.beta.threads.messages.list(thread_id=thread.id)
                    for message in messages.data:
                        if message.role == "assistant":
                            for content in message.content:
                                if content.type == "text":
                                    result = markdown.markdown(content.text.value)
                                    break
                        if result:
                            break

        except Exception as e:
            print("Error:", e)
            result = "Sorry, something went wrong while scheduling. Please try again."

    html_template = load_index_html()
    return render_template_string(html_template, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
