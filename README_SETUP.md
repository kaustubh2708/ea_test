# Momo Executive Assistant - Setup Guide

## 🚀 Quick Setup

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd momo-executive-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Google API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the JSON file and save as `credentials.json` in the project root

### 3. Run the Application
```bash
# Web App (Recommended)
python3 web_app.py

# Or API Server
python3 main.py
```

### 4. Connect Your Gmail
1. Open http://localhost:8000
2. Click "Connect Gmail"
3. Complete OAuth flow
4. See your emails classified automatically!

## 🎯 Features

- **Smart Email Classification**: AI-powered priority scoring
- **Task Detection**: Automatically identifies emails with tasks/meetings
- **Google Calendar Integration**: One-click task scheduling
- **Real-time Dashboard**: Live email summary and statistics
- **Auto-refresh**: Checks for new emails every 5 minutes

## 🔒 Security Note

Never commit `credentials.json` or `token.json` to version control. These files contain your Google API credentials and should be kept private.

## 🛠️ Troubleshooting

- **No emails showing**: Check browser console for errors
- **OAuth issues**: Ensure you're added as a test user in Google Cloud Console
- **Port conflicts**: Change port in web_app.py if 8000 is in use