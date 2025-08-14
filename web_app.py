#!/usr/bin/env python3
"""
Momo Web App - Email Classification & Calendar Integration
Web-based version that works on all systems
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import asyncio

# Gmail and Calendar integration
try:
    from google.auth.transport.requests import Request as GoogleRequest
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Email classification logic
from main import MomoAgent, EmailInput

app = FastAPI(title="Momo Executive Assistant", description="AI-powered email management")

class MomoWebApp:
    def __init__(self):
        self.agent = MomoAgent()
        self.gmail_service = None
        self.calendar_service = None
        self.credentials = None
        self.emails = []
        self.classified_emails = []
        self.is_connected = False
        
    def get_gmail_auth_url(self):
        """Get Gmail OAuth URL"""
        if not GOOGLE_AVAILABLE:
            return None
            
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar'
        ]
        
        if not os.path.exists('credentials.json'):
            return None
            
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.redirect_uri = 'http://localhost:8000/auth/callback'
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def handle_auth_callback(self, code):
        """Handle OAuth callback"""
        try:
            print("Handling OAuth callback...")
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/calendar'
            ]
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8000/auth/callback'
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            print("Got credentials successfully")
            
            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("Saved credentials to token.json")
            
            # Build services
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds
            self.is_connected = True
            
            print("Gmail and Calendar services built successfully")
            
            # Test Gmail connection
            try:
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                print(f"Connected to Gmail account: {profile.get('emailAddress')}")
            except Exception as e:
                print(f"Error testing Gmail connection: {e}")
            
            return True
        except Exception as e:
            print(f"Auth error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_existing_credentials(self):
        """Load existing credentials if available"""
        if os.path.exists('token.json'):
            try:
                SCOPES = [
                    'https://www.googleapis.com/auth/gmail.readonly',
                    'https://www.googleapis.com/auth/calendar'
                ]
                
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
                
                if creds and creds.valid:
                    self.gmail_service = build('gmail', 'v1', credentials=creds)
                    self.calendar_service = build('calendar', 'v3', credentials=creds)
                    self.credentials = creds
                    self.is_connected = True
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())
                    self.gmail_service = build('gmail', 'v1', credentials=creds)
                    self.calendar_service = build('calendar', 'v3', credentials=creds)
                    self.credentials = creds
                    self.is_connected = True
                    
                    # Save refreshed credentials
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                    return True
            except Exception as e:
                print(f"Error loading credentials: {e}")
        
        return False
    
    def fetch_emails(self):
        """Fetch emails from Gmail"""
        if not self.gmail_service:
            print("Gmail service not available")
            return []
        
        try:
            print("Fetching emails from Gmail...")
            # Try a broader query first
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=50, q='newer_than:7d'
            ).execute()
            
            messages = results.get('messages', [])
            print(f"Found {len(messages)} messages")
            
            if not messages:
                # Try without any query
                print("No messages with query, trying without filters...")
                results = self.gmail_service.users().messages().list(
                    userId='me', maxResults=20
                ).execute()
                messages = results.get('messages', [])
                print(f"Found {len(messages)} messages without filters")
            
            self.emails = []
            
            for i, msg in enumerate(messages):
                try:
                    print(f"Processing email {i+1}/{len(messages)}")
                    email_data = self.gmail_service.users().messages().get(
                        userId='me', id=msg['id']
                    ).execute()
                    
                    headers = email_data['payload'].get('headers', [])
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    body = self.extract_email_body(email_data['payload'])
                    
                    email_obj = {
                        'id': msg['id'],
                        'sender': sender,
                        'subject': subject,
                        'body': body,
                        'date': date
                    }
                    
                    self.emails.append(email_obj)
                    print(f"Added email: {subject[:50]}...")
                    
                except Exception as e:
                    print(f"Error processing individual email: {e}")
                    continue
            
            print(f"Successfully processed {len(self.emails)} emails")
            self.classify_emails()
            print(f"Classified {len(self.classified_emails)} emails")
            return self.classified_emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_email_body(self, payload):
        """Extract email body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = self.decode_base64(data)
                    break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = self.decode_base64(data)
        
        return body[:1000]
    
    def decode_base64(self, data):
        """Decode base64 email content"""
        import base64
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    
    def classify_emails(self):
        """Classify fetched emails"""
        self.classified_emails = []
        
        for email in self.emails:
            email_input = EmailInput(
                sender=email['sender'],
                subject=email['subject'],
                content=email['body']
            )
            
            classification = self.agent.classify_email(email_input)
            
            classified_email = {
                **email,
                'priority_score': classification['priority_score'],
                'labels': classification['labels'],
                'is_important': classification['is_important'],
                'has_tasks': self.detect_tasks(email['body'])
            }
            
            self.classified_emails.append(classified_email)
        
        self.classified_emails.sort(key=lambda x: x['priority_score'], reverse=True)
    
    def detect_tasks(self, content):
        """Detect if email contains tasks"""
        task_keywords = [
            'meeting', 'call', 'schedule', 'appointment', 'deadline',
            'due date', 'task', 'action item', 'follow up', 'reminder'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in task_keywords)
    
    def add_to_calendar(self, email_id):
        """Add email task to calendar"""
        if not self.calendar_service:
            return False
        
        email = next((e for e in self.classified_emails if e['id'] == email_id), None)
        if not email:
            return False
        
        event = {
            'summary': f"Task: {email['subject']}",
            'description': f"From: {email['sender']}\n\n{email['body'][:500]}",
            'start': {
                'dateTime': (datetime.now() + timedelta(days=1)).isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
                'timeZone': 'America/New_York',
            },
        }
        
        try:
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            return True
        except Exception as e:
            print(f"Calendar error: {e}")
            return False

# Initialize the app
momo_app = MomoWebApp()

@app.on_event("startup")
async def startup_event():
    # Try to load existing credentials
    momo_app.load_existing_credentials()
    if momo_app.is_connected:
        # Fetch emails in background
        threading.Thread(target=momo_app.fetch_emails, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Momo Executive Assistant</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header h1 { margin: 0; color: #333; }
            .status { display: inline-block; padding: 5px 10px; border-radius: 5px; font-size: 14px; margin-left: 10px; }
            .status.connected { background: #d4edda; color: #155724; }
            .status.disconnected { background: #f8d7da; color: #721c24; }
            .dashboard { display: grid; grid-template-columns: 300px 1fr 300px; gap: 20px; }
            .sidebar, .main-content, .details { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .sidebar h3, .main-content h3, .details h3 { margin-top: 0; color: #333; }
            .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px 0; }
            .btn:hover { background: #0056b3; }
            .btn:disabled { background: #ccc; cursor: not-allowed; }
            .email-list { max-height: 600px; overflow-y: auto; }
            .email-item { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; }
            .email-item:hover { background: #f8f9fa; border-color: #007bff; }
            .email-item.high-priority { border-left: 4px solid #dc3545; }
            .email-item.medium-priority { border-left: 4px solid #ffc107; }
            .email-item.low-priority { border-left: 4px solid #28a745; }
            .email-sender { font-weight: bold; color: #333; }
            .email-subject { color: #666; margin: 5px 0; }
            .email-labels { font-size: 12px; }
            .label { background: #e9ecef; color: #495057; padding: 2px 6px; border-radius: 3px; margin-right: 5px; }
            .priority-score { float: right; font-weight: bold; }
            .summary { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .loading { text-align: center; padding: 40px; color: #666; }
            .email-details { max-height: 500px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
            @media (max-width: 768px) {
                .dashboard { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Momo Executive Assistant</h1>
                <span id="status" class="status disconnected">Not Connected</span>
                <button id="connectBtn" class="btn" onclick="connectGmail()">Connect Gmail</button>
                <button id="refreshBtn" class="btn" onclick="refreshEmails()" disabled>Refresh Emails</button>
            </div>
            
            <div class="dashboard">
                <div class="sidebar">
                    <h3>📊 Summary</h3>
                    <div id="summary" class="summary">
                        <div>📧 Total: 0</div>
                        <div>⭐ Important: 0</div>
                        <div>📅 With Tasks: 0</div>
                    </div>
                    
                    <h3>🏷️ Labels</h3>
                    <div id="labels"></div>
                </div>
                
                <div class="main-content">
                    <h3>📧 Classified Emails</h3>
                    <div id="emailList" class="email-list">
                        <div class="loading">Connect Gmail to see your emails</div>
                    </div>
                </div>
                
                <div class="details">
                    <h3>📄 Email Details</h3>
                    <div id="emailDetails">Select an email to view details</div>
                    <button id="addToCalendar" class="btn" onclick="addToCalendar()" disabled>Add to Calendar</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentEmailId = null;
            let emails = [];
            
            async function connectGmail() {
                try {
                    const response = await fetch('/auth/url');
                    const data = await response.json();
                    
                    if (data.auth_url) {
                        window.open(data.auth_url, '_blank');
                        // Poll for connection status
                        pollConnectionStatus();
                    } else {
                        alert('Please set up Google credentials first. Run: python3 setup_google_auth.py');
                    }
                } catch (error) {
                    alert('Error connecting to Gmail: ' + error.message);
                }
            }
            
            async function pollConnectionStatus() {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch('/status');
                        const data = await response.json();
                        
                        if (data.connected) {
                            clearInterval(interval);
                            updateConnectionStatus(true);
                            refreshEmails();
                        }
                    } catch (error) {
                        console.error('Error checking status:', error);
                    }
                }, 2000);
            }
            
            function updateConnectionStatus(connected) {
                const status = document.getElementById('status');
                const connectBtn = document.getElementById('connectBtn');
                const refreshBtn = document.getElementById('refreshBtn');
                
                if (connected) {
                    status.textContent = 'Connected ✓';
                    status.className = 'status connected';
                    connectBtn.disabled = true;
                    refreshBtn.disabled = false;
                } else {
                    status.textContent = 'Not Connected';
                    status.className = 'status disconnected';
                    connectBtn.disabled = false;
                    refreshBtn.disabled = true;
                }
            }
            
            async function refreshEmails() {
                document.getElementById('emailList').innerHTML = '<div class="loading">Loading emails...</div>';
                
                try {
                    const response = await fetch('/emails');
                    emails = await response.json();
                    displayEmails(emails);
                    updateSummary(emails);
                } catch (error) {
                    document.getElementById('emailList').innerHTML = '<div class="loading">Error loading emails</div>';
                }
            }
            
            function displayEmails(emails) {
                const emailList = document.getElementById('emailList');
                
                if (emails.length === 0) {
                    emailList.innerHTML = '<div class="loading">No emails found</div>';
                    return;
                }
                
                emailList.innerHTML = emails.map(email => {
                    const priorityClass = email.priority_score > 0.7 ? 'high-priority' : 
                                        email.priority_score > 0.5 ? 'medium-priority' : 'low-priority';
                    
                    return `
                        <div class="email-item ${priorityClass}" onclick="selectEmail('${email.id}')">
                            <div class="email-sender">${email.sender.substring(0, 30)}</div>
                            <div class="email-subject">${email.subject}</div>
                            <div class="email-labels">
                                ${email.labels.map(label => `<span class="label">${label}</span>`).join('')}
                                ${email.has_tasks ? '<span class="label" style="background: #007bff; color: white;">📅 Tasks</span>' : ''}
                            </div>
                            <div class="priority-score">${email.priority_score.toFixed(2)}</div>
                        </div>
                    `;
                }).join('');
            }
            
            function selectEmail(emailId) {
                currentEmailId = emailId;
                const email = emails.find(e => e.id === emailId);
                
                if (email) {
                    const details = `From: ${email.sender}
Subject: ${email.subject}
Priority: ${email.priority_score.toFixed(2)}
Labels: ${email.labels.join(', ')}
Has Tasks: ${email.has_tasks ? 'Yes' : 'No'}

Content:
${email.body}`;
                    
                    document.getElementById('emailDetails').innerHTML = `<div class="email-details">${details}</div>`;
                    document.getElementById('addToCalendar').disabled = !email.has_tasks;
                }
            }
            
            function updateSummary(emails) {
                const total = emails.length;
                const important = emails.filter(e => e.is_important).length;
                const withTasks = emails.filter(e => e.has_tasks).length;
                
                document.getElementById('summary').innerHTML = `
                    <div>📧 Total: ${total}</div>
                    <div>⭐ Important: ${important}</div>
                    <div>📅 With Tasks: ${withTasks}</div>
                `;
                
                // Update labels
                const labelCounts = {};
                emails.forEach(email => {
                    email.labels.forEach(label => {
                        labelCounts[label] = (labelCounts[label] || 0) + 1;
                    });
                });
                
                const labelsHtml = Object.entries(labelCounts)
                    .map(([label, count]) => `<div>${label}: ${count}</div>`)
                    .join('');
                
                document.getElementById('labels').innerHTML = labelsHtml;
            }
            
            async function addToCalendar() {
                if (!currentEmailId) return;
                
                try {
                    const response = await fetch(`/calendar/add/${currentEmailId}`, { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('Task added to calendar successfully!');
                    } else {
                        alert('Failed to add to calendar');
                    }
                } catch (error) {
                    alert('Error adding to calendar: ' + error.message);
                }
            }
            
            // Check initial connection status
            fetch('/status').then(response => response.json()).then(data => {
                updateConnectionStatus(data.connected);
                if (data.connected) {
                    refreshEmails();
                }
            });
            
            // Auto-refresh every 5 minutes
            setInterval(() => {
                if (document.getElementById('refreshBtn').disabled === false) {
                    refreshEmails();
                }
            }, 300000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/status")
async def get_status():
    """Get connection status"""
    return {"connected": momo_app.is_connected}

@app.get("/auth/url")
async def get_auth_url():
    """Get Gmail OAuth URL"""
    auth_url = momo_app.get_gmail_auth_url()
    return {"auth_url": auth_url}

@app.get("/auth/callback")
async def auth_callback(code: str):
    """Handle OAuth callback"""
    success = momo_app.handle_auth_callback(code)
    if success:
        return HTMLResponse("""
        <html>
        <body>
        <h2>✅ Successfully connected to Gmail!</h2>
        <p>You can now close this window and return to the main app.</p>
        <script>window.close();</script>
        </body>
        </html>
        """)
    else:
        return HTMLResponse("""
        <html>
        <body>
        <h2>❌ Failed to connect to Gmail</h2>
        <p>Please try again.</p>
        </body>
        </html>
        """)

@app.get("/emails")
async def get_emails():
    """Get classified emails"""
    print("API: Getting emails...")
    if not momo_app.is_connected:
        print("API: Not connected to Gmail")
        return []
    
    # Fetch fresh emails
    emails = momo_app.fetch_emails()
    print(f"API: Returning {len(emails)} emails")
    return emails

@app.post("/calendar/add/{email_id}")
async def add_to_calendar(email_id: str):
    """Add email to calendar"""
    success = momo_app.add_to_calendar(email_id)
    return {"success": success}

@app.get("/debug")
async def debug_info():
    """Debug information"""
    return {
        "connected": momo_app.is_connected,
        "gmail_service": momo_app.gmail_service is not None,
        "calendar_service": momo_app.calendar_service is not None,
        "total_emails": len(momo_app.emails),
        "classified_emails": len(momo_app.classified_emails),
        "credentials_file_exists": os.path.exists('credentials.json'),
        "token_file_exists": os.path.exists('token.json')
    }

if __name__ == "__main__":
    print("🚀 Starting Momo Web App...")
    print("📱 Open your browser to: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)