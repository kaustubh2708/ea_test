# 🤖 Momo Desktop App - Native macOS Email Assistant

A beautiful, native macOS desktop application for intelligent email management with AI-powered summaries.

## 🌟 Features

### 🎯 **Smart Email Classification**
- Automatic priority scoring (0.0 - 1.0)
- Intelligent label generation
- Task detection and highlighting
- Sender importance analysis

### 🤖 **AI-Powered Summaries**
- **Google Gemini 1.5 Flash** integration
- Natural language summaries under 150 words
- Conversational tone, no structured formats
- **FREE tier**: 1,500 requests/day

### 🍎 **Native macOS Experience**
- Clean, modern interface using native macOS styling
- Retina display support
- Aqua theme integration
- Responsive design

### 📧 **Gmail Integration**
- OAuth2 secure authentication
- Real-time email fetching
- Last 3 days of emails
- Auto-refresh every 5 minutes

### 📊 **Intelligent Analytics**
- Overall inbox summary
- Priority breakdown
- Label distribution
- Sender analysis
- Task identification

## 🚀 Quick Start

### Option 1: Easy Launcher
```bash
python launch_desktop.py
```
The launcher will:
- ✅ Check all dependencies
- ✅ Install missing packages
- ✅ Guide you through setup
- ✅ Launch the app

### Option 2: Direct Launch
```bash
python momo_desktop.py
```

### Option 3: macOS App Bundle
```bash
python create_macos_app.py
```
Creates a native `.app` bundle you can double-click!

## 📋 Setup Requirements

### 1. 🐍 Python Requirements
- **Python 3.8+** (3.9+ recommended)
- Built-in `tkinter` (included with Python)

### 2. 📦 Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-generativeai python-dotenv
```

### 3. 🔐 Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json`
5. Place in app folder

### 4. 🤖 Gemini API Key (FREE!)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key (starts with `AIza`)
5. Add to `.env` file:
   ```
   GEMINI_API_KEY=AIzaSyYour-Key-Here
   ```

## 🎨 User Interface

### 📱 **Main Window Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Momo - AI Email Assistant        🤖 Gemini Ready ● Connected │
├─────────────┬─────────────────────────────┬─────────────────┤
│             │                             │                 │
│ 🔗 Connect  │     📧 Classified Emails    │ 📄 Email Details│
│ 🔄 Refresh  │                             │                 │
│             │ 🎯│👤│📝│🏷️│⏰              │ 🤖 AI Summary   │
│ 📊 Summary  │ ──┼──┼──┼──┼──              │                 │
│ • Total: 15 │ 🔴│John│Meeting│work│10:30   │ [Email content  │
│ • Important │ 🟡│Jane│Update│news│09:15    │  and AI summary]│
│ • Tasks: 5  │ 🟢│Bob │Info  │    │08:45    │                 │
│             │                             │                 │
│ 🏷️ Labels   │                             │                 │
│ • work: 8   │                             │                 │
│ • meeting:3 │                             │                 │
│             │                             │                 │
│ 📊 Overall  │                             │                 │
│ Summary     │                             │                 │
└─────────────┴─────────────────────────────┴─────────────────┘
```

### 🎯 **Priority Color Coding**
- 🔴 **High Priority** (0.7+): Urgent, important emails
- 🟡 **Medium Priority** (0.5-0.7): Needs attention
- 🟢 **Low Priority** (<0.5): Regular emails

### 🏷️ **Smart Labels**
- `meeting` - Meetings, calls, appointments
- `urgent` - Time-sensitive content
- `work` - Work-related emails
- `personal` - Personal communications
- `newsletter` - Newsletters, updates
- `finance` - Bills, invoices, payments
- `travel` - Bookings, itineraries

## 🤖 AI Features

### 📝 **Individual Email Summaries**
- Click any email → "🤖 AI Summary"
- Natural language explanation
- Action items highlighted
- Conversational tone
- Under 150 words

### 📊 **Overall Inbox Analysis**
- "📊 Generate Overall Summary" button
- Executive overview of entire inbox
- Priority actions needed
- Key themes and topics
- Sender analysis
- Task summary

### 💡 **Smart Insights**
- Automatic task detection
- Meeting identification
- Deadline recognition
- Sender importance scoring
- Content categorization

## ⚡ Performance

### 🚀 **Speed**
- **Email Fetch**: ~2-3 seconds for 50 emails
- **Classification**: Instant (local processing)
- **AI Summary**: ~1-2 seconds per email
- **UI Updates**: Real-time

### 💰 **Cost**
- **Gmail API**: FREE (generous quotas)
- **Gemini AI**: FREE tier (1,500 requests/day)
- **No billing required** for basic usage

### 🔄 **Rate Limiting**
- 1 second between AI requests
- Automatic caching to avoid duplicates
- Respectful API usage

## 🛠️ Troubleshooting

### ❌ **Common Issues**

**"Google APIs not available"**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**"Gemini not available"**
```bash
pip install google-generativeai python-dotenv
```

**"credentials.json not found"**
- Download from Google Cloud Console
- Enable Gmail API in your project
- Create OAuth 2.0 credentials

**"Gemini API key not found"**
- Get free key at: https://aistudio.google.com/app/apikey
- Add to `.env` file: `GEMINI_API_KEY=AIzaSy...`

**"Connection failed"**
- Check internet connection
- Verify credentials.json is valid
- Try deleting `token.json` and re-authenticating

### 🔍 **Debug Mode**
Run with verbose logging:
```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG); exec(open('momo_desktop.py').read())"
```

## 🔐 Privacy & Security

### ✅ **What We Do**
- Store credentials locally only
- Use OAuth2 for secure authentication
- Cache summaries to reduce API calls
- Process emails on-demand

### ❌ **What We Don't Do**
- Store emails on external servers
- Share data with third parties
- Retain personal information
- Access emails without permission

### 🛡️ **Data Flow**
1. Gmail → Your computer (via Google APIs)
2. Email content → Gemini AI (for summaries only)
3. Summaries cached locally
4. No permanent storage of email content

## 🎯 Use Cases

### 👔 **Business Professionals**
- Quickly triage morning emails
- Identify urgent items first
- Get AI summaries of long emails
- Track meeting requests and deadlines

### 📚 **Students & Academics**
- Manage university communications
- Track assignment deadlines
- Organize research correspondence
- Filter important announcements

### 🏠 **Personal Use**
- Organize family communications
- Track bills and appointments
- Manage newsletter subscriptions
- Stay on top of personal tasks

## 🚀 Advanced Features

### 🔄 **Auto-Refresh**
- Checks for new emails every 5 minutes
- Updates classifications automatically
- Maintains current selection
- Background processing

### 💾 **Caching System**
- AI summaries cached locally
- Avoids duplicate API calls
- Faster subsequent access
- Respects rate limits

### 🎨 **Customization**
- Native macOS appearance
- Retina display support
- Responsive layout
- System theme integration

## 📈 Roadmap

### 🔜 **Coming Soon**
- [ ] Custom label creation
- [ ] Email search and filtering
- [ ] Calendar integration
- [ ] Notification system
- [ ] Dark mode support

### 💡 **Future Ideas**
- [ ] Multiple account support
- [ ] Email templates
- [ ] Automated responses
- [ ] Advanced analytics
- [ ] Plugin system

## 🤝 Contributing

Want to improve Momo Desktop? Here's how:

1. **Report Issues**: Found a bug? Let us know!
2. **Suggest Features**: Have ideas? We'd love to hear them!
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Help improve guides

## 📄 License

This project is open source. See LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for intelligent summaries
- **Gmail API** for email access
- **Python tkinter** for native GUI
- **macOS** for beautiful design inspiration

---

**🎉 Ready to revolutionize your email management with AI?**

Get started with: `python launch_desktop.py`

**Happy emailing!** 📧✨