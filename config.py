import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the IT Help Bot"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # OpenAI settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4o'
    OPENAI_MAX_TOKENS = 1000
    OPENAI_TEMPERATURE = 0.7
    
    # Database settings
    DATABASE_PATH = 'chat.db'
    
    # Security settings
    COMMAND_TIMEOUT = 30  # seconds
    MAX_COMMAND_OUTPUT = 10000  # characters
    
    # WebSocket settings
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Network test settings
    PING_TIMEOUT = 5  # seconds
    DNS_TIMEOUT = 3  # seconds
    
    # Chat settings
    MAX_MESSAGE_LENGTH = 1000
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # Approved commands by OS
    WINDOWS_COMMANDS = [
        'ipconfig', 'ping', 'nslookup', 'systeminfo', 'tasklist',
        'sfc', 'chkdsk', 'netstat', 'tracert', 'route', 'arp',
        'getmac', 'wmic', 'dir', 'type', 'echo'
    ]
    
    MACOS_COMMANDS = [
        'ifconfig', 'ping', 'nslookup', 'system_profiler', 'ps',
        'diskutil', 'netstat', 'traceroute', 'route', 'arp',
        'networksetup', 'scutil', 'ls', 'cat', 'echo', 'df'
    ]
    
    LINUX_COMMANDS = [
        'ifconfig', 'ping', 'nslookup', 'ps', 'df', 'free',
        'netstat', 'traceroute', 'route', 'arp', 'ls', 'cat',
        'echo', 'uname', 'uptime', 'who', 'w', 'top'
    ]
    
    # Command patterns that are always blocked
    BLOCKED_PATTERNS = [
        'rm -rf', 'del /s', 'format', 'fdisk', 'dd',
        'sudo', 'su', 'chmod 777', 'chown root',
        'wget', 'curl', 'nc', 'telnet', 'ssh',
        '> /dev/', '>> /dev/', '| bash', '| sh'
    ] 