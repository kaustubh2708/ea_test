#!/usr/bin/env python3
"""
Test client for Momo Executive Agent
Run this to test the functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_email_classification():
    """Test email classification functionality"""
    print("🧪 Testing Email Classification...")
    
    # Test emails
    test_emails = [
        {
            "sender": "boss@company.com",
            "subject": "URGENT: Client meeting tomorrow",
            "content": "We need to prepare for the important client presentation tomorrow. Please review the proposal and budget numbers."
        },
        {
            "sender": "newsletter@marketing.com", 
            "subject": "Weekly Newsletter - Special Offers Inside!",
            "content": "Check out our latest promotions and sales. Unsubscribe anytime."
        },
        {
            "sender": "john@partner.com",
            "subject": "Contract review needed",
            "content": "Hi, can you review the contract we discussed? The deadline is next week."
        }
    ]
    
    for email in test_emails:
        response = requests.post(f"{BASE_URL}/emails/classify", json=email)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email from {email['sender']}")
            print(f"   Priority: {result['priority_score']:.2f}")
            print(f"   Important: {result['is_important']}")
            print(f"   Labels: {result['labels']}")
            print()
        else:
            print(f"❌ Failed to classify email from {email['sender']}")

def test_important_emails():
    """Test getting important emails"""
    print("📧 Getting Important Emails...")
    
    response = requests.get(f"{BASE_URL}/emails/important")
    if response.status_code == 200:
        result = response.json()
        emails = result['important_emails']
        print(f"Found {len(emails)} important emails:")
        for email in emails:
            print(f"  • {email['subject']} (Score: {email['priority_score']:.2f})")
    else:
        print("❌ Failed to get important emails")
    print()

def test_meeting_scheduling():
    """Test meeting scheduling functionality"""
    print("📅 Testing Meeting Scheduling...")
    
    meeting_request = {
        "title": "Project Review Meeting",
        "duration_minutes": 60,
        "attendee_email": "colleague@company.com",
        "preferred_times": [
            (datetime.now() + timedelta(days=1)).isoformat(),
            (datetime.now() + timedelta(days=2)).isoformat()
        ]
    }
    
    response = requests.post(f"{BASE_URL}/meetings/suggest", json=meeting_request)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Meeting: {result['meeting_title']}")
        print(f"   Duration: {result['duration_minutes']} minutes")
        print("   Suggested times:")
        for time_slot in result['suggested_times']:
            dt = datetime.fromisoformat(time_slot)
            print(f"     • {dt.strftime('%A, %B %d at %I:%M %p')}")
    else:
        print("❌ Failed to get meeting suggestions")
    print()

def test_chat():
    """Test chat functionality"""
    print("💬 Testing Chat Interface...")
    
    messages = [
        "Hello Momo, what can you do?",
        "I need help with my emails",
        "Can you help me schedule a meeting?"
    ]
    
    for msg in messages:
        response = requests.post(f"{BASE_URL}/chat", json={"message": msg})
        if response.status_code == 200:
            result = response.json()
            print(f"👤 You: {msg}")
            print(f"🤖 Momo: {result['response']}")
            print()

def main():
    print("🤖 Testing Momo Executive Agent")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running!")
            print()
        else:
            print("❌ Server responded with error")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
        print("Run: python main.py")
        return
    
    # Run tests
    test_email_classification()
    test_important_emails()
    test_meeting_scheduling()
    test_chat()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()