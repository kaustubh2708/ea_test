#!/usr/bin/env python3
"""
Quick test to verify Momo functionality without running the server
"""

import sys
import os
sys.path.append('.')

from main import MomoAgent, EmailInput

def test_email_classification():
    """Test the email classification logic"""
    print("🧪 Testing Email Classification Logic...")
    
    agent = MomoAgent()
    
    # Test emails
    test_emails = [
        EmailInput(
            sender="boss@company.com",
            subject="URGENT: Client meeting tomorrow",
            content="We need to prepare for the important client presentation tomorrow. Please review the proposal and budget numbers."
        ),
        EmailInput(
            sender="newsletter@marketing.com", 
            subject="Weekly Newsletter - Special Offers Inside!",
            content="Check out our latest promotions and sales. Unsubscribe anytime."
        ),
        EmailInput(
            sender="john@partner.com",
            subject="Contract review needed",
            content="Hi, can you review the contract we discussed? The deadline is next week."
        )
    ]
    
    for email in test_emails:
        result = agent.classify_email(email)
        print(f"✅ Email from {email.sender}")
        print(f"   Subject: {email.subject}")
        print(f"   Priority: {result['priority_score']:.2f}")
        print(f"   Important: {result['is_important']}")
        print(f"   Labels: {result['labels']}")
        print()

def test_meeting_suggestions():
    """Test meeting time suggestions"""
    print("📅 Testing Meeting Time Suggestions...")
    
    agent = MomoAgent()
    
    from main import MeetingRequest
    request = MeetingRequest(
        title="Project Review Meeting",
        duration_minutes=60,
        attendee_email="colleague@company.com",
        preferred_times=[]
    )
    
    suggestions = agent.suggest_meeting_times(request)
    print(f"✅ Meeting: {request.title}")
    print(f"   Duration: {request.duration_minutes} minutes")
    print("   Suggested times:")
    for time_slot in suggestions:
        from datetime import datetime
        dt = datetime.fromisoformat(time_slot)
        print(f"     • {dt.strftime('%A, %B %d at %I:%M %p')}")
    print()

def main():
    print("🤖 Testing Momo Executive Agent Core Logic")
    print("=" * 50)
    
    test_email_classification()
    test_meeting_suggestions()
    
    print("🎉 Core logic tests completed!")
    print("\nTo test the full API:")
    print("1. Run: source venv/bin/activate && python3 main.py")
    print("2. In another terminal: python3 test_client.py")
    print("3. Or visit: http://localhost:8000")

if __name__ == "__main__":
    main()