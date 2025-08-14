# Momo Executive Agent

A local AI-powered executive assistant for email prioritization, scheduling, and productivity management.

## Features

- **Email Classification**: Automatically prioritizes and labels incoming emails
- **Smart Scheduling**: Suggests meeting times across timezones
- **Chat Interface**: Natural language interaction with your assistant
- **Local Database**: All data stored locally for privacy

## Quick Start

### Option 1: Desktop App (Recommended)

1. **Install Dependencies**
   ```bash
   source venv/bin/activate  # or create: python3 -m venv venv
   pip install -r requirements.txt
   ```

2. **Set up Google Integration**
   ```bash
   python3 setup_google_auth.py
   ```

3. **Run Desktop App**
   ```bash
   python3 desktop_app.py
   ```

### Option 2: API Server

1. **Start the Server**
   ```bash
   python3 main.py
   ```

2. **Test the System**
   ```bash
   python3 test_client.py
   ```

## API Endpoints

### Email Classification
```bash
POST /emails/classify
{
  "sender": "boss@company.com",
  "subject": "Important meeting",
  "content": "We need to discuss the quarterly results..."
}
```

### Get Important Emails
```bash
GET /emails/important
```

### Schedule Meetings
```bash
POST /meetings/suggest
{
  "title": "Project Review",
  "duration_minutes": 60,
  "attendee_email": "colleague@company.com",
  "preferred_times": ["2024-01-15T10:00:00"]
}
```

### Chat with Momo
```bash
POST /chat
{
  "message": "Help me prioritize my emails"
}
```

## Web Interface

Visit `http://localhost:8000` to see the API documentation and test the endpoints interactively.

## Next Steps

- Add OpenAI integration for better email classification
- Integrate with Gmail/Outlook APIs
- Add calendar integration
- Build a web frontend
- Add notification system

## Architecture

- **FastAPI**: Web framework for API endpoints
- **SQLite**: Local database for storing emails and preferences
- **Pydantic**: Data validation and serialization
- **OpenAI**: AI-powered classification (optional)

## Privacy

All data is stored locally on your machine. No emails or personal information is sent to external services unless you configure API integrations.

## Desktop App Features

- **Gmail Integration**: Connect your Gmail account to fetch real emails
- **Smart Classification**: Automatically prioritize and label emails
- **Task Detection**: Identify emails containing tasks or meeting requests
- **Calendar Integration**: Add email tasks directly to Google Calendar
- **Real-time Dashboard**: See email summary and priority breakdown
- **Auto-refresh**: Automatically check for new emails every 5 minutes

## Screenshots

The desktop app provides:
- Left sidebar with controls and email summary
- Main area showing classified emails in priority order
- Right panel for email details
- One-click calendar integration for tasks

## Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Gmail API + Calendar API
3. Create OAuth 2.0 credentials for desktop application
4. Download credentials.json and place in project folder
5. Run the app - it will handle OAuth flow automatically