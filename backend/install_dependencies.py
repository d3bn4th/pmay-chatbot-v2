#!/usr/bin/env python3
"""
Script to install the new cachetools dependency for the enhanced chatbot.
"""

import subprocess
import sys
import os

def install_dependency(package_name):
    """Install a Python package using pip."""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    """Main installation function."""
    print("🔧 Installing Enhanced Chatbot Dependencies")
    print("=" * 50)
    
    # List of new dependencies
    dependencies = [
        "cachetools>=5.0.0"
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for dep in dependencies:
        if install_dependency(dep):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"   Successfully installed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run the enhanced chatbot with:")
        print("   cd backend")
        print("   uvicorn api.main:app --reload")
        print("\n🧪 To test the enhancements, run:")
        print("   python test_enhanced_chatbot.py")
    else:
        print("⚠️  Some dependencies failed to install.")
        print("   Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 