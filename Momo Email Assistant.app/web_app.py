#!/usr/bin/env python3
"""
Momo Web App - Email Classification & Calendar Integration
Web-based version that works on all systems
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import asyncio

# Configure comprehensive logging
import logging.handlers

def setup_logging():
    """Setup comprehensive logging system"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Main application log file (rotating)
    app_handler = logging.handlers.RotatingFileHandler(
        'logs/momo_app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(detailed_formatter)
    
    # Error log file (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/momo_errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Gmail API specific log
    gmail_handler = logging.handlers.RotatingFileHandler(
        'logs/gmail_api.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    gmail_handler.setLevel(logging.DEBUG)
    gmail_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Setup specific loggers
    gmail_logger = logging.getLogger('gmail_api')
    gmail_logger.addHandler(gmail_handler)
    gmail_logger.setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

# Initialize logging
logger = setup_logging()
logger.info("🚀 Momo Assistant logging system initialized")

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

# This will be initialized later with lifespan

class MomoWebApp:
    def __init__(self):
        logger.info("🔧 Initializing MomoWebApp...")
        self.agent = MomoAgent()
        self.gmail_service = None
        self.calendar_service = None
        self.credentials = None
        self.emails = []
        self.classified_emails = []
        self.is_connected = False
        
        # Add summary cache and rate limiting
        self.summary_cache = {}  # Cache summaries to avoid re-generating
        self.last_api_call = 0   # Track last OpenAI API call
        self.min_api_interval = 1.0  # Minimum 1 second between API calls
        
        # Initialize Gemini for summarization
        self.gemini_available = False
        try:
            import google.generativeai as genai
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and not api_key.startswith('your_gem'):
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_available = True
                logger.info("✅ Gemini client initialized for email summarization")
            else:
                logger.warning("⚠️ Gemini API key not found or is placeholder. Summarization will use fallback method.")
        except ImportError as e:
            logger.warning(f"⚠️ Gemini not installed: {e}. Summarization will use fallback method.")
        except Exception as e:
            logger.error(f"❌ Error initializing Gemini: {e}")
        
        logger.info("✅ MomoWebApp initialization complete")
        
    def get_gmail_auth_url(self):
        """Get Gmail OAuth URL"""
        gmail_logger = logging.getLogger('gmail_api')
        
        if not GOOGLE_AVAILABLE:
            logger.error("❌ Google APIs not available - missing dependencies")
            return None
            
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar'
        ]
        
        if not os.path.exists('credentials.json'):
            logger.error("❌ credentials.json file not found")
            return None
            
        try:
            gmail_logger.info("🔐 Creating OAuth flow for Gmail authentication")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8000/auth/callback'
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            gmail_logger.info("✅ Successfully generated Gmail auth URL")
            return auth_url
        except Exception as e:
            gmail_logger.error(f"❌ Error creating OAuth flow: {e}")
            return None
    
    def handle_auth_callback(self, code):
        """Handle OAuth callback"""
        gmail_logger = logging.getLogger('gmail_api')
        
        try:
            gmail_logger.info("🔐 Handling OAuth callback...")
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/calendar'
            ]
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8000/auth/callback'
            
            flow.fetch_token(code=code)
            creds = flow.credentials
            gmail_logger.info("✅ Got credentials successfully")
            
            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            gmail_logger.info("💾 Saved credentials to token.json")
            
            # Build services
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds
            self.is_connected = True
            
            gmail_logger.info("🔧 Gmail and Calendar services built successfully")
            
            # Test Gmail connection
            try:
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                email_address = profile.get('emailAddress')
                gmail_logger.info(f"✅ Connected to Gmail account: {email_address}")
                logger.info(f"🎉 Successfully authenticated with Gmail: {email_address}")
            except Exception as e:
                gmail_logger.error(f"❌ Error testing Gmail connection: {e}")
            
            return True
        except Exception as e:
            gmail_logger.error(f"❌ Auth error: {e}")
            logger.error(f"Authentication failed: {e}")
            import traceback
            gmail_logger.debug(traceback.format_exc())
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
        """Fetch emails from Gmail with improved error handling"""
        gmail_logger = logging.getLogger('gmail_api')
        
        if not self.gmail_service:
            logger.error("❌ Gmail service not available")
            return []
        
        try:
            gmail_logger.info("📧 Fetching emails from Gmail...")
            start_time = datetime.now()
            
            # Limit to fewer emails to prevent crashes
            results = self.gmail_service.users().messages().list(
                userId='me', maxResults=20, q='newer_than:3d'
            ).execute()
            
            messages = results.get('messages', [])
            gmail_logger.info(f"📊 Found {len(messages)} messages in last 3 days")
            
            if not messages:
                gmail_logger.info("🔍 No messages with date filter, trying without filters...")
                results = self.gmail_service.users().messages().list(
                    userId='me', maxResults=10
                ).execute()
                messages = results.get('messages', [])
                gmail_logger.info(f"📊 Found {len(messages)} messages without filters")
            
            self.emails = []
            processed_count = 0
            error_count = 0
            
            # Process emails with better error handling and rate limiting
            for i, msg in enumerate(messages[:15]):  # Limit to 15 emails max
                try:
                    gmail_logger.debug(f"📧 Processing email {i+1}/{min(len(messages), 15)}")
                    
                    # Add retry logic with exponential backoff
                    max_retries = 3
                    email_data = None
                    
                    for retry in range(max_retries):
                        try:
                            email_data = self.gmail_service.users().messages().get(
                                userId='me', id=msg['id'], format='full'
                            ).execute()
                            break
                        except Exception as e:
                            if retry < max_retries - 1:
                                wait_time = (2 ** retry)  # Exponential backoff
                                gmail_logger.warning(f"⚠️ API error, retrying in {wait_time}s... ({retry + 1}/{max_retries}): {e}")
                                import time
                                time.sleep(wait_time)
                                continue
                            else:
                                gmail_logger.error(f"❌ Failed to fetch email after {max_retries} retries: {e}")
                                error_count += 1
                                continue
                    
                    if not email_data:
                        continue
                    
                    # Safely extract email data
                    payload = email_data.get('payload', {})
                    headers = payload.get('headers', [])
                    
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    # Extract body with better error handling
                    try:
                        body = self.extract_email_body(payload)
                        gmail_logger.debug(f"📄 Extracted body ({len(body)} chars) from: {subject[:30]}...")
                    except Exception as body_error:
                        gmail_logger.warning(f"⚠️ Error extracting body from '{subject[:30]}...': {body_error}")
                        body = "Could not extract email content"
                    
                    email_obj = {
                        'id': msg['id'],
                        'sender': sender,
                        'subject': subject,
                        'body': body,
                        'date': date
                    }
                    
                    self.emails.append(email_obj)
                    processed_count += 1
                    gmail_logger.info(f"✅ Added email {processed_count}: {subject[:50]}...")
                    
                    # Add small delay to prevent rate limiting
                    import time
                    time.sleep(0.1)
                    
                except Exception as e:
                    gmail_logger.error(f"❌ Error processing email {i+1}: {e}")
                    error_count += 1
                    continue
            
            # Log summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            gmail_logger.info(f"📊 Email fetch complete: {processed_count} processed, {error_count} errors, {duration:.2f}s")
            logger.info(f"✅ Successfully processed {len(self.emails)} emails in {duration:.2f}s")
            
            # Classify emails
            logger.info("🤖 Starting email classification...")
            self.classify_emails()
            logger.info(f"✅ Classified {len(self.classified_emails)} emails")
            
            return self.classified_emails
            
        except Exception as e:
            gmail_logger.error(f"❌ Critical error fetching emails: {e}")
            logger.error(f"Email fetch failed: {e}")
            import traceback
            gmail_logger.debug(traceback.format_exc())
            return []
    
    def extract_email_body(self, payload):
        """Extract email body from Gmail payload with improved handling"""
        body = ""
        
        try:
            if 'parts' in payload:
                # Multi-part email
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type == 'text/plain' and 'data' in part.get('body', {}):
                        data = part['body']['data']
                        body = self.decode_base64(data)
                        break
                    elif mime_type == 'text/html' and not body and 'data' in part.get('body', {}):
                        # Fallback to HTML if no plain text
                        data = part['body']['data']
                        html_body = self.decode_base64(data)
                        # Simple HTML to text conversion
                        import re
                        body = re.sub('<[^<]+?>', '', html_body)
                        
            elif payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
                # Single part plain text
                data = payload['body']['data']
                body = self.decode_base64(data)
                
            elif payload.get('mimeType') == 'text/html' and 'data' in payload.get('body', {}):
                # Single part HTML
                data = payload['body']['data']
                html_body = self.decode_base64(data)
                import re
                body = re.sub('<[^<]+?>', '', html_body)
                
        except Exception as e:
            print(f"Error extracting email body: {e}")
            body = "Could not extract email content"
        
        # Clean and limit body text
        body = body.strip()[:1000] if body else "No content available"
        return body
    
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
        
        # Sort by tasks first, then by priority
        self.classified_emails.sort(key=lambda x: (
            not x['has_tasks'],  # Tasks first (False comes before True)
            -x['priority_score']  # Then by priority (highest first)
        ))
    
    def detect_tasks(self, content):
        """Detect if email contains tasks"""
        task_keywords = [
            'meeting', 'call', 'schedule', 'appointment', 'deadline',
            'due date', 'task', 'action item', 'follow up', 'reminder'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in task_keywords)
    
    def generate_email_summary(self, email):
        """Generate simple text summary under 150 words"""
        email_id = email.get('id', '')
        logger.info(f"🤖 Generating summary for email: {email['subject'][:30]}...")
        
        # Check cache first
        if email_id in self.summary_cache:
            logger.info(f"📋 Using cached summary for: {email['subject'][:30]}...")
            return self.summary_cache[email_id]
        
        try:
            if self.gemini_available:
                # Rate limiting - ensure minimum interval between API calls
                import time
                current_time = time.time()
                time_since_last_call = current_time - self.last_api_call
                
                if time_since_last_call < self.min_api_interval:
                    sleep_time = self.min_api_interval - time_since_last_call
                    logger.info(f"⏱️ Rate limiting: waiting {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                
                # Simple prompt for natural text summary
                prompt = f"""
                Please write a simple, natural summary of this email in under 150 words. 
                Just explain what the email is about in plain English, like you're telling a colleague.

                Subject: {email['subject']}
                From: {email['sender']}
                Content: {email['body'][:1000]}

                Write a clear, conversational summary without using structured formats, bullet points, or labels like "Main Topic" or "Action Required". Just describe what the email says and what needs to be done (if anything).
                """
                
                logger.debug(f"🔍 Sending Gemini request with rate limiting...")
                
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 200,
                        'top_p': 0.8,
                        'top_k': 40
                    }
                )
                
                # Update rate limiting tracker
                self.last_api_call = time.time()
                
                summary = response.text.strip()
                word_count = len(summary.split())
                
                # Cache the summary
                self.summary_cache[email_id] = summary
                
                logger.info(f"✅ Generated Gemini summary ({word_count} words) for: {email['subject'][:30]}...")
                
                return summary
            else:
                # Fallback summarization method
                logger.warning("⚠️ Gemini not available, using fallback summary")
                return self.generate_fallback_summary(email)
                
        except Exception as e:
            logger.error(f"❌ Summarization error for {email['subject'][:30]}...: {e}")
            if "rate_limit" in str(e).lower() or "too many requests" in str(e).lower() or "quota" in str(e).lower():
                logger.warning("⚠️ Rate limit hit, using fallback summary")
            return self.generate_fallback_summary(email)
    
    def generate_fallback_summary(self, email):
        """Generate simple fallback summary without Gemini"""
        logger.info(f"📝 Generating fallback summary for: {email['subject'][:30]}...")
        
        content = email['body'][:400]
        subject = email['subject']
        sender = email['sender']
        
        # Extract sender name
        sender_name = sender.split('<')[0].strip() if '<' in sender else sender.split('@')[0]
        
        # Check for common patterns
        action_keywords = ['please', 'need', 'request', 'action', 'review', 'approve', 'sign', 'meeting', 'call', 'schedule']
        has_action = any(word in content.lower() for word in action_keywords)
        
        # Generate simple, natural summary
        if has_action:
            summary = f"This email from {sender_name} is about {subject.lower()}. Based on the content, it appears to require some action or response from you. The email discusses {content[:100].strip()}{'...' if len(content) > 100 else ''}"
        else:
            summary = f"This is an informational email from {sender_name} regarding {subject.lower()}. The message covers {content[:100].strip()}{'...' if len(content) > 100 else ''}"
        
        word_count = len(summary.split())
        logger.info(f"✅ Generated fallback summary ({word_count} words)")
        
        return summary
        
        return summary.strip()
    
    def generate_overall_summary(self):
        """Generate a comprehensive summary of all emails"""
        if not self.classified_emails:
            return "No emails to summarize."
        
        try:
            if self.gemini_available:
                # Prepare email data for AI analysis
                email_data = []
                for email in self.classified_emails[:10]:  # Limit to top 10 emails
                    email_data.append({
                        'subject': email['subject'],
                        'sender': email['sender'].split('<')[0].strip() if '<' in email['sender'] else email['sender'].split('@')[0],
                        'priority': email['priority_score'],
                        'has_tasks': email['has_tasks'],
                        'labels': email['labels'],
                        'preview': email['body'][:200]
                    })
                
                prompt = f"""
                Analyze these {len(self.classified_emails)} emails and provide a comprehensive executive summary:

                Email Data: {str(email_data)}

                Please provide:
                1. **Executive Overview**: What's the overall situation in my inbox today?
                2. **Priority Actions**: What needs immediate attention?
                3. **Key Themes**: What are the main topics/categories?
                4. **Task Summary**: Meetings, deadlines, and action items
                5. **Sender Analysis**: Who are the key people reaching out?

                Keep it concise but comprehensive, under 200 words.
                """
                
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 250,
                        'top_p': 0.8,
                        'top_k': 40
                    }
                )
                
                return response.text.strip()
            else:
                return self.generate_fallback_overall_summary()
                
        except Exception as e:
            print(f"Overall summarization error: {e}")
            return self.generate_fallback_overall_summary()
    
    def generate_fallback_overall_summary(self):
        """Generate overall summary without AI"""
        total = len(self.classified_emails)
        high_priority = len([e for e in self.classified_emails if e['priority_score'] > 0.7])
        with_tasks = len([e for e in self.classified_emails if e['has_tasks']])
        important = len([e for e in self.classified_emails if e['is_important']])
        
        # Analyze senders
        sender_counts = {}
        for email in self.classified_emails:
            sender = email['sender'].split('<')[0].strip() if '<' in email['sender'] else email['sender'].split('@')[0]
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze labels
        label_counts = {}
        for email in self.classified_emails:
            for label in email['labels']:
                label_counts[label] = label_counts.get(label, 0) + 1
        
        top_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get urgent emails
        urgent_emails = [e for e in self.classified_emails if e['priority_score'] > 0.8][:3]
        
        summary = f"""**Executive Overview**: You have {total} emails today with {high_priority} high-priority items requiring attention.

**Priority Actions**: 
• {high_priority} high-priority emails need immediate review
• {with_tasks} emails contain tasks or meeting requests
• {important} emails marked as important

**Key Themes**: 
{' • '.join([f"{label} ({count})" for label, count in top_labels]) if top_labels else "• General correspondence"}

**Task Summary**: {with_tasks} emails contain actionable items including meetings, deadlines, or follow-ups.

**Top Senders**: 
{' • '.join([f"{sender} ({count})" for sender, count in top_senders]) if top_senders else "• Various senders"}

**Urgent Items**: 
{' • '.join([f"{email['subject'][:40]}..." for email in urgent_emails]) if urgent_emails else "• No urgent items"}"""
        
        return summary
    
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

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🔄 Initializing Momo Assistant...")
    logger.info(f"📊 Logs will be stored in: {os.path.abspath('logs/')}")
    
    momo_app.load_existing_credentials()
    if momo_app.is_connected:
        logger.info("📧 Connected to Gmail, fetching emails in background...")
        # Fetch emails in background with better error handling
        def safe_fetch():
            try:
                momo_app.fetch_emails()
            except Exception as e:
                logger.error(f"❌ Background email fetch error: {e}")
        
        threading.Thread(target=safe_fetch, daemon=True).start()
    else:
        logger.warning("⚠️ Not connected to Gmail. Please authenticate first.")
    
    logger.info("✅ Momo Assistant startup complete")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Momo Assistant...")
    logger.info("👋 Goodbye!")

# Initialize app with lifespan
app = FastAPI(
    title="Momo Executive Assistant", 
    description="AI-powered email management",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    """Serve the main dashboard"""
    return FileResponse("static/index.html")

@app.get("/logs-viewer")
async def logs_viewer():
    """Serve the logs viewer page"""
    return FileResponse("static/logs.html")

@app.get("/status")
async def get_status():
    """Get connection status"""
    return {"connected": momo_app.is_connected}

@app.get("/auth/url")
async def get_auth_url():
    """Get Gmail OAuth URL"""
    try:
        auth_url = momo_app.get_gmail_auth_url()
        print(f"Generated auth URL: {auth_url is not None}")
        return {"auth_url": auth_url}
    except Exception as e:
        print(f"Error generating auth URL: {e}")
        return {"auth_url": None, "error": str(e)}

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
    """Get classified emails with error handling"""
    logger.info("🌐 API: /emails endpoint called")
    try:
        if not momo_app.is_connected:
            logger.warning("⚠️ API: Not connected to Gmail")
            return {"error": "Not connected to Gmail", "emails": []}
        
        # Return cached emails if available, otherwise fetch fresh
        if momo_app.classified_emails:
            logger.info(f"📧 API: Returning {len(momo_app.classified_emails)} cached emails")
            return momo_app.classified_emails
        
        # Fetch fresh emails
        logger.info("🔄 API: Fetching fresh emails...")
        emails = momo_app.fetch_emails()
        logger.info(f"✅ API: Returning {len(emails)} fresh emails")
        return emails
        
    except Exception as e:
        logger.error(f"❌ API Error in /emails: {e}")
        return {"error": str(e), "emails": []}

@app.get("/summary/overall")
async def get_overall_summary():
    """Get comprehensive summary of all emails"""
    if not momo_app.is_connected:
        return {"error": "Not connected to Gmail"}
    
    if not momo_app.classified_emails:
        return {"summary": "No emails to summarize.", "generated_with_ai": False}
    
    summary = momo_app.generate_overall_summary()
    return {
        "summary": summary,
        "generated_with_ai": momo_app.gemini_available,
        "total_emails": len(momo_app.classified_emails),
        "high_priority": len([e for e in momo_app.classified_emails if e['priority_score'] > 0.7]),
        "with_tasks": len([e for e in momo_app.classified_emails if e['has_tasks']]),
        "important": len([e for e in momo_app.classified_emails if e['is_important']])
    }

@app.post("/calendar/add/{email_id}")
async def add_to_calendar(email_id: str):
    """Add email to calendar"""
    success = momo_app.add_to_calendar(email_id)
    return {"success": success}

@app.get("/email/summary/{email_id}")
async def get_email_summary(email_id: str):
    """Get AI summary of specific email"""
    logger.info(f"🤖 API: Generating summary for email {email_id[:8]}...")
    
    email = next((e for e in momo_app.classified_emails if e['id'] == email_id), None)
    if not email:
        logger.warning(f"⚠️ Email not found: {email_id[:8]}...")
        return {"error": "Email not found"}
    
    try:
        summary = momo_app.generate_email_summary(email)
        logger.info(f"✅ Generated summary for '{email['subject'][:30]}...' using {'AI' if momo_app.gemini_available else 'fallback'}")
        return {
            "email_id": email_id,
            "summary": summary,
            "generated_with_ai": momo_app.gemini_available
        }
    except Exception as e:
        logger.error(f"❌ Error generating summary for {email_id[:8]}...: {e}")
        return {"error": f"Failed to generate summary: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "gmail": momo_app.is_connected,
            "gemini": momo_app.gemini_available,
            "email_count": len(momo_app.classified_emails)
        }
    }

@app.get("/logs")
async def get_logs(log_type: str = "app", lines: int = 100):
    """Get application logs"""
    logger.info(f"📋 API: Fetching {log_type} logs (last {lines} lines)")
    
    log_files = {
        "app": "logs/momo_app.log",
        "errors": "logs/momo_errors.log", 
        "gmail": "logs/gmail_api.log"
    }
    
    if log_type not in log_files:
        return {"error": f"Invalid log type. Available: {list(log_files.keys())}"}
    
    log_file = log_files[log_type]
    
    try:
        if not os.path.exists(log_file):
            return {"logs": [], "message": f"Log file {log_file} not found"}
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        return {
            "log_type": log_type,
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines),
            "logs": [line.strip() for line in recent_lines]
        }
    except Exception as e:
        logger.error(f"❌ Error reading log file {log_file}: {e}")
        return {"error": f"Failed to read log file: {str(e)}"}

@app.post("/clear-cache")
async def clear_summary_cache():
    """Clear the summary cache"""
    logger.info("�️A API: Clearing summary cache")
    cache_size = len(momo_app.summary_cache)
    momo_app.summary_cache.clear()
    return {"message": f"Cleared {cache_size} cached summaries"}

@app.get("/debug")
async def debug_info():
    """Debug information"""
    logger.info("🔍 API: Debug info requested")
    
    # Get log file sizes
    log_sizes = {}
    for log_name, log_path in [("app", "logs/momo_app.log"), ("errors", "logs/momo_errors.log"), ("gmail", "logs/gmail_api.log")]:
        try:
            if os.path.exists(log_path):
                size = os.path.getsize(log_path)
                log_sizes[log_name] = f"{size / 1024:.1f} KB"
            else:
                log_sizes[log_name] = "Not found"
        except:
            log_sizes[log_name] = "Error"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "connected": momo_app.is_connected,
            "gmail_service": momo_app.gmail_service is not None,
            "calendar_service": momo_app.calendar_service is not None,
            "gemini_available": momo_app.gemini_available,
        },
        "data": {
            "total_emails": len(momo_app.emails),
            "classified_emails": len(momo_app.classified_emails),
            "cached_summaries": len(momo_app.summary_cache),
        },
        "files": {
            "credentials_exists": os.path.exists('credentials.json'),
            "token_exists": os.path.exists('token.json'),
        },
        "logs": log_sizes,
        "rate_limiting": {
            "last_api_call": momo_app.last_api_call,
            "min_interval": momo_app.min_api_interval
        }
    }

if __name__ == "__main__":
    import os
    
    # Configuration from environment variables
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info("🚀 Starting Momo Web App...")
    logger.info(f"📱 Main Dashboard: http://localhost:{PORT}")
    logger.info(f"📋 Logs Viewer: http://localhost:{PORT}/logs-viewer")
    logger.info(f"🔧 Debug mode: {DEBUG}")
    logger.info(f"📊 Logs directory: {os.path.abspath('logs/')}")
    
    uvicorn.run(
        app, 
        host=HOST, 
        port=PORT, 
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )