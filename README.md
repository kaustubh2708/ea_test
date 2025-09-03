# 🤖 Momo Executive Assistant

An AI-powered email assistant that helps you prioritize, classify, and manage your emails efficiently with a beautiful modern interface.

## ✨ Features

### 🎯 **Smart Email Management**
- **Automatic Classification**: AI categorizes emails by importance and type
- **Priority Scoring**: Color-coded priorities (🔴🟡🟢) to focus on what matters
- **Task Detection**: Identifies emails with meetings, deadlines, and action items
- **Label Generation**: Smart categorization with custom labels

### 🤖 **AI-Powered Intelligence**
- **Email Summaries**: Conversational summaries under 150 words
- **Daily Briefing**: Overall inbox analysis and insights
- **Natural Language**: Easy-to-understand explanations
- **Context Awareness**: Understands email relationships and importance

### 📱 **Beautiful Interfaces**
- **Modern Web App**: Gradient design with glassmorphism effects
- **Native Desktop App**: Stunning tkinter interface matching web design
- **Responsive Layout**: Three-panel dashboard for optimal workflow
- **Real-time Updates**: Live statistics and auto-refresh

### 📅 **Calendar Integration**
- **Smart Task Detection**: Finds meetings and deadlines automatically
- **One-Click Scheduling**: Add email tasks to Google Calendar
- **Time Zone Support**: Proper scheduling across time zones

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Setup Google APIs**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project and enable Gmail API + Google Calendar API
- Create OAuth 2.0 credentials and download as `credentials.json`
- Place `credentials.json` in project root

### 3. **Setup Gemini AI** (Recommended)
- Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create `.env` file:
  ```
  GEMINI_API_KEY=your_api_key_here
  ```

### 4. **Launch Application**

#### **🌐 Web Version** (Recommended)
```bash
python web_app.py
```
Open http://localhost:8000

#### **🖥️ Desktop Version**
```bash
python momo_desktop.py
```

#### **🚀 Quick Test**
```bash
python quick_test.py
```

## 🎨 Interface Preview

### **Web App Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Momo Executive Assistant        ● Connected ✓  [Connect] │
├─────────────┬─────────────────────────────┬─────────────────┤
│ 📊 Stats    │     📧 Classified Emails    │ 🤖 AI Summary  │
│ 📧 Total: 15│ 🔴 0.85 │ John   │ Meeting │ ✨ AI SUMMARY   │
│ ⭐ Important│ 🟡 0.65 │ Jane   │ Update  │                 │
│ 📅 Tasks: 5 │ 🟢 0.45 │ Bob    │ Info    │ This email is   │
│             │                             │ about a project │
│ 🤖 Briefing │                             │ meeting...      │
│ You have 15 │                             │                 │
│ emails today│                             │ 📅 Add Calendar │
│ 3 need      │                             │ 🔄 Regenerate   │
│ attention   │                             │                 │
└─────────────┴─────────────────────────────┴─────────────────┘
```

### **Key Features**
- **Color-coded priorities**: Red (urgent), Yellow (medium), Green (low)
- **Smart indicators**: 📅 for tasks, ⭐ for important emails
- **Real-time AI summaries**: Click any email for instant analysis
- **Beautiful gradients**: Modern purple-blue background
- **Professional typography**: Clean, readable fonts

## 📁 Project Structure

```
momo-assistant/
├── 🎯 Core Application
│   ├── main.py              # Email classification engine
│   ├── web_app.py           # Web interface (FastAPI)
│   └── momo_desktop.py      # Desktop app (tkinter)
├── 🎨 Frontend Assets
│   ├── static/
│   │   ├── index.html       # Web app interface
│   │   ├── styles.css       # Modern styling
│   │   └── app.js          # Interactive features
├── 🛠️ Utilities
│   ├── launch_desktop.py    # Desktop launcher with checks
│   ├── quick_test.py        # Quick functionality test
│   └── setup_google_auth.py # Google API setup helper
├── 📚 Documentation
│   ├── README.md           # This file
│   ├── CHANGELOG.md        # Version history
│   ├── DESKTOP_README.md   # Desktop app guide
│   ├── DESKTOP_UI_UPDATE.md # UI transformation log
│   └── GEMINI_SETUP.md     # AI setup guide
└── ⚙️ Configuration
    ├── requirements.txt     # Dependencies
    ├── .env.example        # Environment template
    ├── credentials.json    # Google credentials (you create)
    └── .env               # Your API keys (you create)
```

## 🎯 Usage Guide

### **First Time Setup**
1. **Connect Gmail**: Click "Connect Gmail" → Authorize in browser
2. **Verify AI**: Check "✨ AI Ready" status in interface
3. **Fetch Emails**: Click "Refresh Emails" to load recent messages

### **Daily Workflow**
1. **Check Dashboard**: View priority breakdown and daily briefing
2. **Focus on Red Emails**: Handle high-priority items first
3. **Use AI Summaries**: Click emails for quick understanding
4. **Schedule Tasks**: Add meetings/deadlines to calendar
5. **Monitor Labels**: Track email categories and trends

### **Pro Tips**
- **Auto-refresh**: Emails update every 5 minutes automatically
- **Smart caching**: AI summaries are cached to save API calls
- **Keyboard shortcuts**: Use arrow keys to navigate email list
- **Batch processing**: Handle similar emails together using labels

## 🔧 Technical Requirements

- **Python**: 3.8+ (3.9+ recommended)
- **Google Cloud**: Project with Gmail/Calendar APIs enabled
- **Gemini API**: For AI summaries (optional but recommended)
- **Storage**: ~50MB for application + logs
- **Memory**: ~100MB RAM during operation
- **Network**: Internet connection for API calls

## 🎉 What's New

### **v2.0 - Beautiful UI Transformation**
- ✅ **Stunning modern interface** matching web app design
- ✅ **Fixed all desktop launch issues**
- ✅ **Color-coded email priorities** (🔴🟡🟢)
- ✅ **Real-time AI summaries** with loading animations
- ✅ **Professional typography** and spacing
- ✅ **Gradient backgrounds** and glassmorphism effects

### **v1.0 - Core Features**
- ✅ **Email classification** with priority scoring
- ✅ **Google APIs integration** (Gmail + Calendar)
- ✅ **AI-powered summaries** with Gemini
- ✅ **Web and desktop interfaces**
- ✅ **Task detection** and calendar integration

## 📄 License

MIT License - Feel free to use and modify!