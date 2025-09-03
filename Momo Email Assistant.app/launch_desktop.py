#!/usr/bin/env python3
"""
🚀 Momo Desktop App Launcher
Easy launcher with dependency checking and setup guidance
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    return True

def check_dependency(package_name, install_command=None):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} not installed")
        if install_command:
            print(f"   Install with: {install_command}")
        return False
    else:
        print(f"✅ {package_name} available")
        return True

def check_dependencies():
    """Check all required dependencies"""
    print("🔍 Checking dependencies...")
    
    all_good = True
    
    # Core dependencies
    deps = [
        ("tkinter", "Built-in with Python"),
        ("google.auth", "pip install google-auth"),
        ("google.oauth2", "pip install google-auth-oauthlib"),
        ("googleapiclient", "pip install google-api-python-client"),
        ("google.generativeai", "pip install google-generativeai"),
        ("dotenv", "pip install python-dotenv")
    ]
    
    for package, install_cmd in deps:
        if not check_dependency(package, install_cmd):
            all_good = False
    
    return all_good

def check_credentials():
    """Check if credentials are set up"""
    print("\n🔐 Checking credentials...")
    
    # Check for credentials.json
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
    else:
        print("❌ credentials.json not found")
        print("   Download from Google Cloud Console")
        return False
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check for Gemini API key
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key and not gemini_key.startswith('your_gem'):
                print("✅ Gemini API key configured")
            else:
                print("⚠️  Gemini API key not configured")
                print("   Get free key at: https://aistudio.google.com/app/apikey")
        except:
            print("⚠️  Could not check Gemini API key")
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and configure")
    
    return True

def install_missing_dependencies():
    """Install missing dependencies"""
    print("\n📦 Installing missing dependencies...")
    
    try:
        # Install core packages
        packages = [
            "google-api-python-client",
            "google-auth-httplib2", 
            "google-auth-oauthlib",
            "google-generativeai",
            "python-dotenv"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        print("✅ All dependencies installed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def show_setup_guide():
    """Show setup guide for missing components"""
    print("\n" + "="*60)
    print("🛠️  SETUP GUIDE")
    print("="*60)
    
    print("\n1. 📋 GOOGLE CREDENTIALS:")
    print("   • Go to: https://console.cloud.google.com/")
    print("   • Create a new project or select existing")
    print("   • Enable Gmail API and Google Calendar API")
    print("   • Create OAuth 2.0 credentials")
    print("   • Download as 'credentials.json'")
    print("   • Place in this folder")
    
    print("\n2. 🤖 GEMINI API KEY (FREE):")
    print("   • Go to: https://aistudio.google.com/app/apikey")
    print("   • Sign in with Google account")
    print("   • Click 'Create API Key'")
    print("   • Copy the key (starts with 'AIza')")
    
    print("\n3. 🔧 ENVIRONMENT SETUP:")
    print("   • Copy .env.example to .env")
    print("   • Add your Gemini API key:")
    print("     GEMINI_API_KEY=AIzaSyYour-Key-Here")
    
    print("\n4. 🚀 LAUNCH:")
    print("   • Run this script again")
    print("   • Or run: python momo_desktop.py")
    
    print("\n💡 Benefits:")
    print("   • FREE Gemini AI: 1,500 requests/day")
    print("   • No billing required")
    print("   • Smart email classification")
    print("   • AI-powered summaries")
    
    print("="*60)

def main():
    """Main launcher function"""
    print("🤖 Momo Desktop App Launcher")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❓ Install missing dependencies? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            if install_missing_dependencies():
                print("✅ Dependencies installed! Please restart the launcher.")
                return
            else:
                print("❌ Failed to install dependencies")
                show_setup_guide()
                return
        else:
            show_setup_guide()
            return
    
    # Check credentials
    creds_ok = check_credentials()
    
    if not creds_ok:
        show_setup_guide()
        return
    
    # Launch the app
    print("\n🚀 Launching Momo Desktop App...")
    print("   Close this window to stop the app")
    print("   Check the app window for status updates")
    
    try:
        # Import and run the desktop app
        import subprocess
        result = subprocess.run([sys.executable, "momo_desktop.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running desktop app: {e}")
    except FileNotFoundError:
        print("❌ momo_desktop.py not found in current directory")
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        print("\n🛠️  Troubleshooting:")
        print("   • Check that all dependencies are installed")
        print("   • Verify credentials.json exists")
        print("   • Check .env file configuration")
        print("   • Try running: python momo_desktop.py directly")

if __name__ == "__main__":
    main()