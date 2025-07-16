#!/usr/bin/env python3
"""
IT Help Bot Installation Script
Automates the setup process for the IT Help Bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print the installation banner"""
    print("🤖 IT Help Bot - Installation Script")
    print("=" * 40)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("📋 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_environment():
    """Set up environment configuration"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your OpenAI API key")
        else:
            print("❌ env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        'static/css',
        'static/js', 
        'templates',
        'modules',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")
    return True

def run_tests():
    """Run basic tests to verify installation"""
    print("\n🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "tests/test_basic.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("⚠️  Some tests failed, but installation can continue")
            print(result.stderr)
            return True  # Continue anyway
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return True  # Continue anyway

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your OpenAI API key")
    print("2. Run the application: python run.py")
    print("3. Open your browser to: http://localhost:5000")
    print("\n🔗 Get your OpenAI API key from: https://platform.openai.com/api-keys")
    print("\n📚 For more information, see the README.md file")

def main():
    """Main installation function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed.")
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()

if __name__ == '__main__':
    main() 