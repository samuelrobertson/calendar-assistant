from flask import Flask, request, render_template_string
import openai
import os
import json
import time
import requests
import markdown

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("assistant_id.json") as f:
    assistant_id = json.load(f)["assistant_id"]

GOOGLE_ACCESS_TOKEN = None
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

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
        tokens = res.json()
        GOOGLE_ACCESS_TOKEN = tokens["access_token"]
        return True
    return False

def create_event_in_calendar(summary, start, end, tags):
    if not GOOGLE_ACCESS_TOKEN:
        refresh_google_token()

    def ensure_timezone(dt_string):
        if "Z" in dt_string or "+" in dt_string:
            return dt_string
        return dt_string + "-07:00"

    headers = {
        "Authorization": f"Bearer {GOOGLE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    event_data = {
        "summary": summary,
        "start": {"dateTime": ensure_timezone(start), "timeZone": "America/Los_Angeles"},
        "end": {"dateTime": ensure_timezone(end), "timeZone": "America/Los_Angeles"},
        "description": ", ".join(tags) if tags else ""
    }

    res = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=event_data)

    if res.status_code == 401:
        refresh_google_token()
        headers["Authorization"] = f"Bearer {GOOGLE_ACCESS_TOKEN}"
        res = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", headers=headers, json=event_data)

    if res.status_code in [200, 201]:
        event = res.json()
        return {
            "status": "success",
            "summary": event.get("summary"),
            "start": event.get("start", {}).get("dateTime"),
            "link": event.get("htmlLink")
        }
    else:
        return { "status": "error", "detail": res.text }

with open("index.html") as f:
    html_template = f.read()

@app.route("/", methods=["GET", "POST"])
def index():
    reply = None
    if request.method == "POST":
        user_input = request.form.get("event_text")
        if user_input:
            thread = openai.beta.threads.create()
            openai.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_input)
            run = openai.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
            start_time = time.time()
            timeout = 20

            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run_status.status == "completed":
                    break
                elif run_status.status == "requires_action":
                    for call in run_status.required_action.submit_tool_outputs.tool_calls:
                        if call.function.name == "create_calendar_event":
                            args = json.loads(call.function.arguments)
                            result = create_event_in_calendar(args.get("summary"), args.get("start"), args.get("end"), args.get("tags", []))
                            openai.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=[{"tool_call_id": call.id, "output": json.dumps(result)}]
                            )
                elif time.time() - start_time > timeout:
                    reply = "Assistant timed out."
                    break
                time.sleep(1)

            if not reply:
                messages = openai.beta.threads.messages.list(thread_id=thread.id)
                for message in messages.data:
                    if message.role == "assistant":
                        for content in message.content:
                            if content.type == "text":
                                reply = markdown.markdown(content.text.value or "")
                                break
                        if reply:
                            break

    return render_template_string(html_template, result=reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
