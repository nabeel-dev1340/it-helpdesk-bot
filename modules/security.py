import re
import logging
from config import Config

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation for command execution and input sanitization"""
    
    def __init__(self):
        """Initialize security validator"""
        self.blocked_patterns = Config.BLOCKED_PATTERNS
        self.windows_commands = Config.WINDOWS_COMMANDS
        self.macos_commands = Config.MACOS_COMMANDS
    
    def is_command_safe(self, command):
        """Check if a command is safe to execute"""
        if not command or not isinstance(command, str):
            return False
        
        command_lower = command.lower().strip()
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if pattern.lower() in command_lower:
                logger.warning(f"Blocked command pattern detected: {pattern}")
                return False
        
        # Check for dangerous shell operators
        dangerous_operators = ['&&', '||', ';', '|', '>', '>>', '<', '<<', '`', '$(']
        for operator in dangerous_operators:
            if operator in command:
                logger.warning(f"Dangerous shell operator detected: {operator}")
                return False
        
        # Check for file system traversal attempts
        traversal_patterns = ['../', '..\\', '/etc/', '/var/', '/usr/', 'C:\\Windows\\']
        for pattern in traversal_patterns:
            if pattern.lower() in command_lower:
                logger.warning(f"File system traversal attempt detected: {pattern}")
                return False
        
        # Check for network-related dangerous commands
        network_dangerous = ['nc', 'netcat', 'telnet', 'ssh', 'wget', 'curl', 'ftp']
        for cmd in network_dangerous:
            if cmd in command_lower:
                logger.warning(f"Dangerous network command detected: {cmd}")
                return False
        
        # Check for privilege escalation attempts
        privilege_patterns = ['sudo', 'su', 'runas', 'elevate', 'admin']
        for pattern in privilege_patterns:
            if pattern in command_lower:
                logger.warning(f"Privilege escalation attempt detected: {pattern}")
                return False
        
        return True
    
    def validate_command_for_os(self, command, os_type):
        """Validate command for specific operating system"""
        if not self.is_command_safe(command):
            return False
        
        command_lower = command.lower().strip()
        
        # Get approved commands for the OS
        if os_type.lower() == 'windows':
            approved_commands = self.windows_commands
        elif os_type.lower() in ['macos', 'darwin']:
            approved_commands = self.macos_commands
        else:
            # For Linux, use a subset of safe commands
            approved_commands = [
                'ifconfig', 'ping', 'nslookup', 'ps', 'netstat',
                'df', 'free', 'uptime', 'who', 'w', 'ls', 'cat'
            ]
        
        # Check if command starts with an approved command
        for approved_cmd in approved_commands:
            if command_lower.startswith(approved_cmd):
                return True
        
        logger.warning(f"Command not in approved list for {os_type}: {command}")
        return False
    
    def sanitize_input(self, user_input):
        """Sanitize user input to prevent injection attacks"""
        if not user_input:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '|', ';', '`', '$', '(', ')']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Limit length
        if len(sanitized) > Config.MAX_MESSAGE_LENGTH:
            sanitized = sanitized[:Config.MAX_MESSAGE_LENGTH]
        
        return sanitized.strip()
    
    def validate_file_path(self, file_path):
        """Validate file path to prevent directory traversal"""
        if not file_path:
            return False
        
        # Check for directory traversal attempts
        dangerous_patterns = ['../', '..\\', '/etc/', '/var/', '/usr/', 'C:\\Windows\\']
        file_path_lower = file_path.lower()
        
        for pattern in dangerous_patterns:
            if pattern in file_path_lower:
                return False
        
        # Check for absolute paths (only allow relative paths)
        if file_path.startswith('/') or file_path.startswith('C:\\'):
            return False
        
        return True
    
    def log_security_event(self, event_type, details):
        """Log security events for audit purposes"""
        logger.warning(f"SECURITY EVENT - {event_type}: {details}")
    
    def check_rate_limit(self, user_id, action_type):
        """Check rate limiting for user actions"""
        # Simple rate limiting - can be enhanced with Redis or database
        # For now, just log the action
        logger.info(f"Rate limit check for user {user_id}, action: {action_type}")
        return True
    
    def validate_api_key(self, api_key):
        """Validate API key format and security"""
        if not api_key:
            return False
        
        # Check if API key looks like a valid OpenAI key
        if not api_key.startswith('sk-'):
            return False
        
        # Check length (OpenAI keys are typically 51 characters)
        if len(api_key) < 20 or len(api_key) > 100:
            return False
        
        return True
    
    def get_safe_commands_for_os(self, os_type):
        """Get list of safe commands for the specified OS"""
        if os_type.lower() == 'windows':
            return self.windows_commands
        elif os_type.lower() in ['macos', 'darwin']:
            return self.macos_commands
        else:
            return [
                'ifconfig', 'ping', 'nslookup', 'ps', 'netstat',
                'df', 'free', 'uptime', 'who', 'w', 'ls', 'cat'
            ]
    
    def is_network_command(self, command):
        """Check if command is network-related"""
        network_commands = ['ping', 'nslookup', 'ipconfig', 'ifconfig', 'netstat', 'tracert', 'traceroute']
        command_lower = command.lower()
        
        for net_cmd in network_commands:
            if net_cmd in command_lower:
                return True
        
        return False
    
    def is_system_command(self, command):
        """Check if command is system-related"""
        system_commands = ['systeminfo', 'system_profiler', 'tasklist', 'ps', 'df', 'free']
        command_lower = command.lower()
        
        for sys_cmd in system_commands:
            if sys_cmd in command_lower:
                return True
        
        return False 