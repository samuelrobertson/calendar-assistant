# Calendar Agent

**Calendar Agent** is a smart assistant that helps users schedule Google Calendar events using natural language — powered by OpenAI’s Assistants API with RAG (retrieval-augmented generation) using a team schedule file.

It automatically chooses the earliest available weekday time slot and responds with a clickable Google Calendar link.

## Live Demo

Try it here:  
[https://calendar-agent-samrobertson6.replit.app](https://calendar-agent-samrobertson6.replit.app)

## Default Example Prompt

When the page loads, it’s pre-filled with this example input:

Schedule a 15-minute meeting between Sam and Lisa on the earliest available Friday

Users can modify the request in natural language, for example:
- “Schedule a 30-minute sync for tomorrow morning”
- “Find a time next week for Sam and Lisa outside working hours”
- “Set up a 45-minute meeting after 4 PM PT next Monday”

## How It Works

- Uses OpenAI Assistants API with a custom tool function (`create_calendar_event`)
- Injects today’s date via `instructions` dynamically in each request
- Uploads and references a static RAG file (`team_schedule.md`) to define recurring team availability
- When a tool function is called, the app programmatically builds a link and inserts it as a Markdown-formatted hyperlink
- Flask + TailwindCSS frontend displays results and links cleanly, with Markdown rendering enabled

## Included RAG File

The included file `team_schedule.md` defines working hours, recurring meetings, and blocked times for the team.  
You can edit this file to match your own organization’s recurring schedule or availability policies.

## Credits

Created by **Sam Robertson**  
Built using Flask, OpenAI Assistants API, TailwindCSS, and Google Calendar integration
