# Calendar Assistant Agent

👉 [Try the Live Demo](https://calendar-agent-samrobertson6.replit.app/)

This project is a natural language AI assistant that creates real events in your Google Calendar using OpenAI's Assistants API and Flask.

## Features

- Interprets plain English like “Lunch Friday at 1pm”
- Schedules real calendar events via Google Calendar API
- Returns a clickable calendar link in response
- Includes a clean UI with Tailwind CSS and a loading spinner
- Uses OpenAI’s Assistants API and Tool Calling
- Automatically refreshes OAuth tokens

## Technologies

- Python 3.11
- Flask
- OpenAI Assistants API (GPT-4)
- Google OAuth2 + Calendar API
- Jinja2 Templates
- Tailwind CSS

## Setup Instructions

1. Create a Google Cloud project and enable Calendar API
2. Get your OAuth2 client ID and secret
3. Set up the following Replit secrets:
   - `OPENAI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
4. Run `create_calendar_assistant.py` to register the assistant
5. Paste the assistant ID into `assistant_id.json`
6. Run `app.py` and open your Replit public URL

## License

MIT License
