#!/usr/bin/env python3
"""
IT Help Bot Startup Script
A simple script to run the IT Help Bot application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask-socketio', 'openai',
        'psutil', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All required packages are installed")

def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("Creating .env file from template...")
        
        if Path('env.example').exists():
            import shutil
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your OpenAI API key")
        else:
            print("❌ env.example file not found")
            sys.exit(1)
    else:
        print("✅ .env file found")
    
    # Check for OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-api-key-here':
        print("⚠️  Warning: OpenAI API key not configured")
        print("Please set your OpenAI API key in the .env file")
        print("You can get an API key from: https://platform.openai.com/api-keys")
    else:
        print("✅ OpenAI API key configured")

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['static/css', 'static/js', 'templates', 'modules', 'tests']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure verified")

def run_application():
    """Run the Flask application"""
    print("\n🚀 Starting IT Help Bot...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the app
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 IT Help Bot stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🤖 IT Help Bot Startup")
    print("=" * 30)
    
    # Run checks
    check_python_version()
    check_dependencies()
    check_environment()
    create_directories()
    
    # Start the application
    run_application()

if __name__ == '__main__':
    main() 