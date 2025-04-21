import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

assistant = openai.beta.assistants.create(
    name="Calendar Agent",
    instructions="""You are a helpful assistant that helps schedule calendar events.

When you create a calendar event using the tool, always use the 'link' field from the tool output in your reply. Never generate a link yourself—just display the one provided as a clickable link like: [View event](https://calendar.google.com/...).""",
    model="gpt-4-1106-preview",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "create_calendar_event",
                "description": "Create a calendar event with summary, time, and optional tags",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Title of the event"
                        },
                        "start": {
                            "type": "string",
                            "description": "ISO 8601 start time"
                        },
                        "end": {
                            "type": "string",
                            "description": "ISO 8601 end time"
                        },
                        "tags": {
                            "type": "array",
                            "items": { "type": "string" },
                            "description": "Optional tags for context"
                        }
                    },
                    "required": ["summary", "start", "end"]
                }
            }
        }
    ]
)

print("Assistant ID:", assistant.id)
