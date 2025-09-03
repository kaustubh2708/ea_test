#!/usr/bin/env python3
"""
🍎 Create macOS App Bundle for Momo Desktop
Creates a native .app bundle that can be launched from Finder
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_app_bundle():
    """Create a macOS .app bundle"""
    
    app_name = "Momo Email Assistant"
    bundle_name = f"{app_name}.app"
    
    print(f"🍎 Creating macOS app bundle: {bundle_name}")
    
    # Create app bundle structure
    bundle_path = Path(bundle_name)
    contents_path = bundle_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Remove existing bundle
    if bundle_path.exists():
        shutil.rmtree(bundle_path)
    
    # Create directories
    macos_path.mkdir(parents=True)
    resources_path.mkdir(parents=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>momo_launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.momo.email-assistant</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>MOMO</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Email</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
    </array>
</dict>
</plist>"""
    
    with open(contents_path / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # Create launcher script
    launcher_script = f"""#!/bin/bash
# Momo Email Assistant Launcher

# Get the directory of this script
DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
BUNDLE_DIR="$DIR/../.."

# Change to bundle directory
cd "$BUNDLE_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    osascript -e 'display dialog "Python 3 is required but not installed. Please install Python 3 from python.org" buttons {{"OK"}} default button "OK" with icon stop'
    exit 1
fi

# Launch the app
$PYTHON_CMD launch_desktop.py

# If launch fails, show error
if [ $? -ne 0 ]; then
    osascript -e 'display dialog "Failed to launch Momo Email Assistant. Please check the terminal for error details." buttons {{"OK"}} default button "OK" with icon stop'
fi
"""
    
    launcher_path = macos_path / "momo_launcher"
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # Make launcher executable
    os.chmod(launcher_path, 0o755)
    
    # Copy application files to bundle
    files_to_copy = [
        "momo_desktop.py",
        "launch_desktop.py",
        "web_app.py",
        "main.py",
        "requirements.txt",
        ".env.example",
        "GEMINI_SETUP.md",
        "CHANGELOG.md"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, bundle_path)
            print(f"  ✅ Copied {file_name}")
    
    # Copy credentials if they exist
    if os.path.exists("credentials.json"):
        shutil.copy2("credentials.json", bundle_path)
        print("  ✅ Copied credentials.json")
    
    if os.path.exists(".env"):
        shutil.copy2(".env", bundle_path)
        print("  ✅ Copied .env")
    
    # Copy static files if they exist
    if os.path.exists("static"):
        shutil.copytree("static", bundle_path / "static")
        print("  ✅ Copied static folder")
    
    # Create app icon (if we had one)
    # For now, we'll use the system default
    
    print(f"✅ Created {bundle_name}")
    print(f"📁 Location: {os.path.abspath(bundle_name)}")
    print("\n🚀 To use:")
    print(f"   1. Double-click {bundle_name} in Finder")
    print("   2. Or drag it to Applications folder")
    print("   3. First launch may ask for permissions")
    
    return bundle_path

def create_dmg():
    """Create a DMG installer (optional)"""
    try:
        print("\n💿 Creating DMG installer...")
        
        dmg_name = "Momo-Email-Assistant-Installer.dmg"
        
        # Remove existing DMG
        if os.path.exists(dmg_name):
            os.remove(dmg_name)
        
        # Create DMG
        subprocess.run([
            "hdiutil", "create", 
            "-volname", "Momo Email Assistant",
            "-srcfolder", "Momo Email Assistant.app",
            "-ov", "-format", "UDZO",
            dmg_name
        ], check=True)
        
        print(f"✅ Created {dmg_name}")
        print("   Users can drag the app to Applications folder")
        
    except subprocess.CalledProcessError:
        print("⚠️  Could not create DMG (hdiutil not available)")
    except FileNotFoundError:
        print("⚠️  Could not create DMG (hdiutil not found)")

def main():
    """Main function"""
    print("🍎 Momo macOS App Bundle Creator")
    print("="*50)
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("❌ This script is for macOS only")
        return
    
    # Create app bundle
    bundle_path = create_app_bundle()
    
    # Ask if user wants DMG
    print(f"\n❓ Create DMG installer? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        create_dmg()
    
    print("\n🎉 macOS app bundle created successfully!")
    print("\n📋 Next steps:")
    print("   1. Double-click the .app to launch")
    print("   2. Follow setup guide for Gmail credentials")
    print("   3. Add Gemini API key for AI features")
    print("   4. Enjoy smart email management!")
    
    print(f"\n💡 The app bundle contains all necessary files")
    print(f"   You can move '{bundle_path.name}' anywhere on your Mac")

if __name__ == "__main__":
    main()