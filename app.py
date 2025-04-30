from flask import Flask, request, render_template
import openai
import os
import json
import time
import markdown
from datetime import datetime

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("assistant_id.json") as f:
    assistant_id = json.load(f)["assistant_id"]

DEFAULT_INPUT = "Schedule a 15-minute meeting between Sam and Lisa on the earliest available Friday"

@app.route("/", methods=["GET", "POST"])
def index():
    reply = None
    user_input = DEFAULT_INPUT

    if request.method == "POST":
        user_input = request.form["user_input"]

        thread = openai.beta.threads.create()

        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        today = datetime.now().strftime("%A, %B %d, %Y")
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=f"Today is {today}."
        )

        start_time = time.time()
        while time.time() - start_time < 90:
            run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status in ["completed", "requires_action", "failed", "cancelled", "expired"]:
                break
            time.sleep(1)

        if run.status == "requires_action":
            tool_outputs = []
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "create_calendar_event":
                    args = json.loads(tool_call.function.arguments)
                    calendar_link = f"https://calendar.google.com/calendar/u/0/r/eventedit?text={args['summary']}&dates={args['start'].replace(':', '').replace('-', '')}/{args['end'].replace(':', '').replace('-', '')}"
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": f"Here's your event: [View on Google Calendar]({calendar_link})"
                    })

            run = openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

            while time.time() - start_time < 90:
                run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run.status == "completed":
                    break
                time.sleep(1)

        if run.status != "completed":
            reply = f"Assistant did not complete. Status: {run.status}"
        else:
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            reply = markdown.markdown(content.text.value)
                            break
                if reply:
                    break

    return render_template("index.html", default_input=user_input, reply=reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
