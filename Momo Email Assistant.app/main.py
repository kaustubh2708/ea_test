#!/usr/bin/env python3
"""
Momo Executive Agent - Local Version
A personal assistant for email prioritization and scheduling
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Momo Executive Agent", version="1.0.0")

# Database setup
def init_db():
    conn = sqlite3.connect('momo.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            priority_score REAL DEFAULT 0.0,
            labels TEXT DEFAULT '',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_important BOOLEAN DEFAULT FALSE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            timezone TEXT DEFAULT 'UTC',
            attendees TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Pydantic models
class EmailInput(BaseModel):
    sender: str
    subject: str
    content: str

class EmailResponse(BaseModel):
    id: int
    sender: str
    subject: str
    priority_score: float
    labels: List[str]
    is_important: bool

class MeetingRequest(BaseModel):
    title: str
    duration_minutes: int
    attendee_email: str
    preferred_times: List[str]  # ISO format strings

# Core agent logic
class MomoAgent:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        
    def classify_email(self, email: EmailInput) -> Dict:
        """Classify email importance using simple heuristics and keywords"""
        
        # Simple keyword-based classification (replace with Gemini later)
        important_keywords = [
            'urgent', 'asap', 'deadline', 'meeting', 'call', 'interview',
            'contract', 'proposal', 'budget', 'revenue', 'client', 'customer'
        ]
        
        low_priority_keywords = [
            'newsletter', 'unsubscribe', 'promotion', 'sale', 'offer',
            'marketing', 'spam', 'advertisement'
        ]
        
        content_lower = (email.subject + ' ' + email.content).lower()
        
        # Calculate priority score
        priority_score = 0.5  # baseline
        
        for keyword in important_keywords:
            if keyword in content_lower:
                priority_score += 0.2
                
        for keyword in low_priority_keywords:
            if keyword in content_lower:
                priority_score -= 0.3
                
        priority_score = max(0.0, min(1.0, priority_score))
        
        # Generate labels
        labels = []
        if priority_score > 0.7:
            labels.append('high-priority')
        if 'meeting' in content_lower or 'call' in content_lower:
            labels.append('scheduling')
        if any(word in content_lower for word in ['client', 'customer', 'proposal']):
            labels.append('business')
            
        return {
            'priority_score': priority_score,
            'labels': labels,
            'is_important': priority_score > 0.6
        }
    
    def suggest_meeting_times(self, request: MeetingRequest) -> List[str]:
        """Suggest available meeting times"""
        # Simple time suggestion logic
        now = datetime.now()
        suggestions = []
        
        # Suggest next 5 business days, 9 AM to 5 PM
        for day_offset in range(1, 6):
            date = now + timedelta(days=day_offset)
            if date.weekday() < 5:  # Monday to Friday
                for hour in [9, 11, 14, 16]:  # 9 AM, 11 AM, 2 PM, 4 PM
                    meeting_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    suggestions.append(meeting_time.isoformat())
                    
        return suggestions[:5]  # Return top 5 suggestions

# Initialize agent
agent = MomoAgent()

@app.on_event("startup")
async def startup_event():
    init_db()
    print("🤖 Momo Executive Agent is starting up...")
    print("📧 Email classification ready")
    print("📅 Scheduling assistant ready")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Momo Executive Agent",
        "version": "1.0.0",
        "features": ["email_classification", "scheduling", "reminders"]
    }

@app.post("/emails/classify", response_model=EmailResponse)
async def classify_email(email: EmailInput):
    """Classify an incoming email and store it"""
    
    # Classify the email
    classification = agent.classify_email(email)
    
    # Store in database
    conn = sqlite3.connect('momo.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO emails (sender, subject, content, priority_score, labels, is_important)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        email.sender,
        email.subject,
        email.content,
        classification['priority_score'],
        ','.join(classification['labels']),
        classification['is_important']
    ))
    
    email_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return EmailResponse(
        id=email_id,
        sender=email.sender,
        subject=email.subject,
        priority_score=classification['priority_score'],
        labels=classification['labels'],
        is_important=classification['is_important']
    )

@app.get("/emails/important")
async def get_important_emails():
    """Get all important emails"""
    conn = sqlite3.connect('momo.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, sender, subject, priority_score, labels, timestamp
        FROM emails 
        WHERE is_important = TRUE 
        ORDER BY priority_score DESC, timestamp DESC
        LIMIT 20
    ''')
    
    emails = []
    for row in cursor.fetchall():
        emails.append({
            'id': row[0],
            'sender': row[1],
            'subject': row[2],
            'priority_score': row[3],
            'labels': row[4].split(',') if row[4] else [],
            'timestamp': row[5]
        })
    
    conn.close()
    return {'important_emails': emails}

@app.post("/meetings/suggest")
async def suggest_meeting_times(request: MeetingRequest):
    """Suggest available meeting times"""
    suggestions = agent.suggest_meeting_times(request)
    
    return {
        'meeting_title': request.title,
        'duration_minutes': request.duration_minutes,
        'suggested_times': suggestions,
        'message': f'Here are 5 available time slots for your {request.duration_minutes}-minute meeting'
    }

@app.post("/chat")
async def chat_with_momo(message: dict):
    """Simple chat interface with Momo"""
    user_message = message.get('message', '')
    
    # Simple response logic (can be enhanced with Gemini)
    if 'email' in user_message.lower():
        return {'response': 'I can help you classify and prioritize your emails. Send them to /emails/classify endpoint.'}
    elif 'meeting' in user_message.lower() or 'schedule' in user_message.lower():
        return {'response': 'I can suggest meeting times for you. Use the /meetings/suggest endpoint with your requirements.'}
    else:
        return {'response': 'I\'m Momo, your executive assistant. I can help with email prioritization and scheduling. What would you like to do?'}

if __name__ == "__main__":
    print("🚀 Starting Momo Executive Agent...")
    uvicorn.run(app, host="0.0.0.0", port=8000)