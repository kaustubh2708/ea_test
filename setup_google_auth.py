#!/usr/bin/env python3
"""
Google API Setup Helper
Run this to set up Google Gmail and Calendar integration
"""

import webbrowser
import os

def setup_google_credentials():
    """Guide user through Google API setup"""
    
    print("🔧 Setting up Google API Integration")
    print("=" * 50)
    
    if os.path.exists('credentials.json'):
        print("✅ credentials.json already exists!")
        return True
    
    print("""
To use Gmail and Calendar integration, you need to:

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project (or select existing one)
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'
5. Choose 'Desktop application'
6. Download the JSON file and rename it to 'credentials.json'
7. Place it in this folder

Would you like me to open Google Cloud Console for you? (y/n): """)
    
    choice = input().lower().strip()
    if choice == 'y':
        webbrowser.open('https://console.cloud.google.com/')
        print("\n📝 Steps to follow in Google Cloud Console:")
        print("1. Create/select project")
        print("2. Enable Gmail API and Calendar API")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download and save as 'credentials.json'")
        print("\nPress Enter when you've downloaded credentials.json...")
        input()
        
        if os.path.exists('credentials.json'):
            print("✅ credentials.json found! You're ready to go.")
            return True
        else:
            print("❌ credentials.json not found. Please try again.")
            return False
    
    print("\n📋 Manual setup instructions:")
    print("1. Visit: https://console.cloud.google.com/")
    print("2. Enable Gmail API and Calendar API")
    print("3. Create OAuth credentials for desktop app")
    print("4. Download as 'credentials.json' in this folder")
    
    return False

def main():
    if setup_google_credentials():
        print("\n🎉 Setup complete! You can now run:")
        print("python3 desktop_app.py")
    else:
        print("\n⚠️  Setup incomplete. Please follow the instructions above.")

if __name__ == "__main__":
    main()