# Calendar Agent Demo

This is a smart AI-powered calendar assistant built with OpenAI Assistants API and Google Calendar integration.

It allows users to submit **plain English scheduling requests** like:

> "Schedule a meeting between Sam and Lisa at the earliest possible time."

The agent will:
- Understand the user's intent
- Infer appropriate weekdays and times automatically
- Search reference schedules via **retrieval augmented generation (RAG)**
- **Create a real Google Calendar event** without asking for confirmation
- Return a **friendly, clear success message** with title, scheduled time, and a clickable calendar link

---

## Key Features

- **OpenAI Assistants API (beta)**
  - Threads, Runs, Tool Calls, File Search (`file_search`)
- **Google Calendar API Integration**
  - OAuth2 secure authentication
  - Real event creation in the user's calendar
- **Real-time Awareness**
  - Dynamically injects today's date
  - Correctly handles current year and scheduling window
- **Business Rule Enforcement**
  - Schedules only Monday–Friday by default
  - Prioritizes normal business hours (9:00 AM–5:00 PM)
- **Friendly UI and Output**
  - Live spinner while processing
  - Clear formatted event summaries
  - Clickable Google Calendar links
- **Robust Production Code**
  - OAuth token refresh
  - Fast polling for assistant responses
  - Graceful error handling

---

## Technologies Used

- Python 3.11
- Flask
- OpenAI Python SDK (`>=1.3.5`)
- Google OAuth2 and Calendar API
- Markdown rendering
- Deployed using Replit Cloud (or portable to Vercel, Render, Fly.io)

---

## Example Prompts

- "Schedule a meeting between Sam and Lisa at the earliest possible time."
- "Book a sync for the engineering team after the daily standup."
- "Find an open time tomorrow afternoon for a 30-minute customer call."
- "Set up a follow-up meeting for Nina and Jose next week."
- "Arrange a kickoff meeting for the project team."

_(No need to specify avoiding weekends — the assistant automatically prefers weekdays during business hours.)_

---

## Included RAG Data File (`team_schedule.md`)

```markdown
# Weekly Team Schedule

- Monday
  - 9:00 AM – Engineering Standup
  - 1:00 PM – Marketing Review

- Tuesday
  - 10:00 AM – Product Sync
  - 2:00 PM – Customer Success Meeting

- Wednesday
  - 9:30 AM – Engineering Standup
  - 11:00 AM – Sales Pipeline Review

- Thursday
  - 9:00 AM – Engineering Standup
  - 3:00 PM – Partner Check-in

- Friday
  - 9:00 AM – Engineering Standup
  - 12:00 PM – Weekly Wrap-up Meeting

# Company Meeting Policy

- Meetings are scheduled Monday through Friday only.
- No meetings are scheduled on weekends (Saturday/Sunday) unless explicitly requested.
- Preferred hours are 9:00 AM to 5:00 PM local time.
