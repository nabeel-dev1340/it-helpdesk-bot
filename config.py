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
    
    # Quick tool optimizations
    QUICK_COMMAND_TIMEOUT = 10  # seconds for fast commands
    MEDIUM_COMMAND_TIMEOUT = 15  # seconds for medium commands
    SLOW_COMMAND_TIMEOUT = 30  # seconds for slow commands
    CACHE_TIMEOUT = 30  # seconds for command caching
    
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
        # Network commands
        'ipconfig', 'ping', 'nslookup', 'netstat', 'tracert', 'route', 'arp',
        'getmac', 'netsh', 'netstat -an', 'ipconfig /flushdns',
        
        # System commands
        'systeminfo', 'tasklist', 'sfc', 'chkdsk', 'dir', 'type', 'echo',
        'wmic', 'systeminfo', 'ver', 'hostname', 'whoami', 'pwd',
        
        # Hardware commands
        'wmic printer list brief', 'wmic logicaldisk get size,freespace,caption',
        'wmic cpu get name', 'wmic memorychip get capacity', 'wmic bios get version',
        'wmic path win32_pnpentity get name,status', 'devmgmt.msc',
        'wmic sounddev get name', 'wmic diskdrive get size',
        
        # Performance commands
        'tasklist /v', 'wmic process get name,processid,workingsetsize',
        'wmic cpu get loadpercentage', 'perfmon', 'resmon',
        
        # Security commands
        'sfc /scannow', 'DISM /Online /Cleanup-Image /RestoreHealth',
        'wmic qfe get hotfixid', 'gpresult /r',
        
        # File system commands
        'dir C:\\ /s', 'tree', 'attrib', 'copy', 'move', 'del',
        
        # Service commands
        'sc query', 'net start', 'net stop', 'services.msc',
        
        # Registry commands
        'reg query', 'reg add', 'reg delete',
        
        # User management
        'net user', 'net localgroup', 'whoami /all',
        
        # Event logs
        'wevtutil qe system', 'wevtutil qe application',
        
        # Power management
        'powercfg /list', 'powercfg /query',
        
        # Network diagnostics
        'netsh wlan show profiles', 'netsh interface show interface',
        'netsh advfirewall show allprofiles'
    ]
    
    MACOS_COMMANDS = [
        # Network commands
        'ifconfig', 'ping', 'nslookup', 'netstat', 'traceroute', 'route', 'arp',
        'networksetup', 'scutil', 'airport', 'netstat -an',
        
        # System commands
        'system_profiler', 'ps', 'df', 'free', 'ls', 'cat', 'echo',
        'uname', 'hostname', 'whoami', 'pwd', 'sw_vers',
        
        # Hardware commands
        'system_profiler SPHardwareDataType', 'system_profiler SPUSBDataType',
        'system_profiler SPAudioDataType', 'system_profiler SPDisplaysDataType',
        'ioreg', 'diskutil list', 'diskutil info',
        
        # Performance commands
        'ps aux --sort=-%cpu | head -20', 'top -l 1', 'vm_stat',
        'iostat', 'netstat -i', 'lsof -i',
        
        # Security commands
        'sudo /usr/libexec/repair_packages --verify', 'system_profiler SPSoftwareDataType',
        'sudo /usr/libexec/repair_packages --verify --standard-pkgs',
        
        # File system commands
        'ls -la', 'du -sh', 'find', 'cp', 'mv', 'rm',
        
        # Service commands
        'launchctl list', 'sudo launchctl load', 'sudo launchctl unload',
        
        # User management
        'dscl . list /Users', 'id', 'groups',
        
        # System logs
        'log show', 'sudo log show --predicate',
        
        # Power management
        'pmset -g', 'pmset -g therm', 'pmset -g batt',
        
        # Network diagnostics
        'networksetup -listallnetworkservices', 'networksetup -getinfo',
        'sudo dscacheutil -flushcache', 'sudo killall -HUP mDNSResponder',
        
        # Additional macOS commands that may require sudo
        'sudo system_profiler', 'sudo diskutil', 'sudo ioreg',
        'sudo networksetup', 'sudo launchctl', 'sudo dscacheutil',
        'sudo killall', 'sudo repair_packages', 'sudo log show',
        'sudo pmset', 'sudo iostat', 'sudo vm_stat',
        
        # Printer commands
        'lpstat -p', 'lpstat -a', 'lpstat -d',
        'system_profiler SPPrintersDataType',
        
        # Audio commands
        'system_profiler SPAudioDataType', 'system_profiler SPAudioDevicesDataType',
        
        # Bluetooth commands
        'system_profiler SPBluetoothDataType',
        
        # Firewall commands
        'sudo /usr/libexec/ApplicationFirewall/socketfilterfw',
        
        # System integrity protection
        'csrutil status',
        
        # Gatekeeper status
        'spctl --status',
        
        # XProtect status
        'system_profiler SPInstallHistoryDataType'
    ]
    
    LINUX_COMMANDS = [
        # Network commands
        'ifconfig', 'ping', 'nslookup', 'ps', 'df', 'free',
        'netstat', 'traceroute', 'route', 'arp', 'ip addr',
        
        # System commands
        'uname', 'uptime', 'who', 'w', 'top', 'ls', 'cat',
        'echo', 'ps aux', 'df -h', 'free -h',
        
        # Hardware commands
        'lscpu', 'lsmem', 'lspci', 'lsusb', 'lshw',
        'cat /proc/cpuinfo', 'cat /proc/meminfo',
        
        # Performance commands
        'ps aux --sort=-%cpu | head -20', 'top -n 1',
        'vmstat', 'iostat', 'netstat -i',
        
        # Security commands
        'sudo apt update', 'sudo apt upgrade', 'sudo clamscan --recursive',
        'sudo chkrootkit', 'sudo rkhunter --check',
        
        # File system commands
        'ls -la', 'du -sh', 'find', 'cp', 'mv', 'rm',
        
        # Service commands
        'systemctl status', 'systemctl list-units', 'service --status-all',
        
        # User management
        'cat /etc/passwd', 'id', 'groups', 'who',
        
        # System logs
        'journalctl', 'dmesg', 'tail -f /var/log/syslog',
        
        # Power management
        'upower -i /org/freedesktop/UPower/devices/battery_BAT0',
        
        # Network diagnostics
        'nmcli device status', 'nmcli connection show',
        'systemctl restart systemd-resolved'
    ]
    
    # Command patterns that are always blocked
    BLOCKED_PATTERNS = [
        'rm -rf', 'del /s', 'format', 'fdisk', 'dd',
        'sudo', 'su', 'chmod 777', 'chown root',
        'wget', 'curl', 'nc', 'telnet', 'ssh',
        '> /dev/', '>> /dev/', '| bash', '| sh'
    ] 