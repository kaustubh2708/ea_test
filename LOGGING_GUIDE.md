# 📋 Momo Assistant - Logging System Guide

## 🎯 Overview

The Momo Assistant now includes a comprehensive logging system to help you monitor application performance, debug issues, and track all operations.

## 📁 Log Files Location

All logs are stored in the `logs/` directory:

```
logs/
├── momo_app.log      # Main application logs (all levels)
├── momo_errors.log   # Error logs only
└── gmail_api.log     # Gmail API specific logs
```

## 🔍 Log Levels

- **DEBUG** 🔍 - Detailed information for debugging
- **INFO** ℹ️ - General information about application flow
- **WARNING** ⚠️ - Warning messages (potential issues)
- **ERROR** ❌ - Error messages (actual problems)

## 📊 Log Format

Each log entry includes:
```
2025-08-28 12:34:28 | logger_name | LEVEL | function:line | message
```

Example:
```
2025-08-28 12:34:28 | gmail_api | INFO | fetch_emails:145 | ✅ Added email: Important Meeting...
```

## 🌐 Web-Based Log Viewer

Access the logs through your browser:

1. **Main Dashboard**: `http://localhost:8000`
2. **Logs Viewer**: `http://localhost:8000/logs-viewer`

### Features:
- ✅ Real-time log viewing
- ✅ Filter by log type (App, Errors, Gmail API)
- ✅ Auto-refresh every 5 seconds
- ✅ Color-coded log levels
- ✅ Adjustable number of lines (50-500)
- ✅ Clear display function

## 🔧 API Endpoints for Logs

### Get Logs
```
GET /logs?log_type=app&lines=100
```

Parameters:
- `log_type`: `app`, `errors`, or `gmail`
- `lines`: Number of recent lines to return (default: 100)

### Debug Information
```
GET /debug
```

Returns system status and log file information.

### Health Check
```
GET /health
```

Returns application health status.

## 📈 What Gets Logged

### Application Events
- ✅ Startup and shutdown
- ✅ Component initialization
- ✅ Configuration loading
- ✅ Error handling

### Gmail API Operations
- ✅ Authentication attempts
- ✅ Email fetching operations
- ✅ API rate limiting
- ✅ Connection issues
- ✅ Email processing details

### Web API Requests
- ✅ Endpoint access
- ✅ Request processing
- ✅ Response generation
- ✅ Error responses

### AI Operations
- ✅ OpenAI API calls
- ✅ Email summarization
- ✅ Classification results
- ✅ Fallback operations

## 🔄 Log Rotation

Logs automatically rotate to prevent disk space issues:

- **Main App Log**: 10MB max, 5 backup files
- **Error Log**: 5MB max, 3 backup files  
- **Gmail API Log**: 5MB max, 3 backup files

## 🛠️ Troubleshooting

### Common Log Patterns

**Successful Email Fetch:**
```
✅ Connected to Gmail account: user@example.com
📧 Fetching emails from Gmail...
📊 Found 15 messages in last 3 days
✅ Added email 1: Important Meeting...
📊 Email fetch complete: 15 processed, 0 errors, 2.34s
```

**Authentication Issues:**
```
❌ credentials.json file not found
⚠️ OpenAI API key not found or is placeholder
❌ Auth error: invalid_grant
```

**API Errors:**
```
⚠️ API error, retrying in 2s... (1/3): SSL error
❌ Failed to fetch email after 3 retries
```

### Monitoring Tips

1. **Check Error Logs First**: `logs/momo_errors.log`
2. **Monitor Gmail API**: `logs/gmail_api.log` for rate limiting
3. **Use Web Viewer**: Real-time monitoring at `/logs-viewer`
4. **Enable Auto-refresh**: For continuous monitoring

## 🚀 Performance Monitoring

The logs include timing information:
- Email fetch duration
- API response times
- Processing statistics

Example:
```
📊 Email fetch complete: 15 processed, 0 errors, 2.34s
✅ Generated summary for 'Meeting Request...' using AI
```

## 🔐 Security Notes

- Logs may contain email subjects and sender information
- API keys are masked in logs
- Personal email content is truncated
- Log files are stored locally only

## 📞 Support

If you encounter issues:

1. Check the error logs: `logs/momo_errors.log`
2. Use the debug endpoint: `GET /debug`
3. Enable debug mode: Set `DEBUG=true` in environment
4. Check the web log viewer for real-time issues

---

**Happy Monitoring!** 📊✨