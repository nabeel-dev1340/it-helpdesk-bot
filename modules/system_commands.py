import subprocess
import platform
import logging
import psutil
from config import Config

logger = logging.getLogger(__name__)

class SystemCommands:
    """Handles safe execution of system commands"""
    
    def __init__(self):
        """Initialize system commands handler"""
        self.os_type = platform.system().lower()
    
    def execute_command(self, command):
        """Execute a system command safely with timeout and validation"""
        try:
            # Validate command before execution
            if not self._is_command_safe(command):
                return {
                    'success': False,
                    'output': 'Command not allowed for security reasons',
                    'error': 'Security validation failed'
                }
            
            # Execute command with timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=Config.COMMAND_TIMEOUT
            )
            
            # Truncate output if too long
            output = result.stdout
            if len(output) > Config.MAX_COMMAND_OUTPUT:
                output = output[:Config.MAX_COMMAND_OUTPUT] + "\n... (output truncated)"
            
            return {
                'success': result.returncode == 0,
                'output': output,
                'error': result.stderr if result.stderr else None,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {Config.COMMAND_TIMEOUT} seconds'
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': f'Command execution failed: {str(e)}'
            }
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': self._get_disk_usage()
            }
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {'error': str(e)}
    
    def _get_disk_usage(self):
        """Get disk usage information"""
        try:
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except PermissionError:
                    continue
            return disk_usage
        except Exception as e:
            logger.error(f"Error getting disk usage: {str(e)}")
            return {}
    
    def _is_command_safe(self, command):
        """Check if command is safe to execute"""
        command_lower = command.lower()
        
        # Check for blocked patterns
        for pattern in Config.BLOCKED_PATTERNS:
            if pattern.lower() in command_lower:
                logger.warning(f"Blocked command pattern detected: {pattern}")
                return False
        
        # Check against approved commands for the OS
        if self.os_type == 'windows':
            approved_commands = Config.WINDOWS_COMMANDS
        elif self.os_type == 'darwin':  # macOS
            approved_commands = Config.MACOS_COMMANDS
        else:
            # For Linux, use the configured commands
            approved_commands = Config.LINUX_COMMANDS
        
        # Check if command starts with an approved command
        for approved_cmd in approved_commands:
            if command_lower.startswith(approved_cmd):
                return True
        
        logger.warning(f"Command not in approved list: {command}")
        return False
    
    def get_network_info(self):
        """Get network interface information"""
        try:
            network_info = {}
            for interface, addresses in psutil.net_if_addrs().items():
                network_info[interface] = []
                for addr in addresses:
                    if addr.family == psutil.AF_INET:  # IPv4
                        network_info[interface].append({
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'family': 'IPv4'
                        })
            return network_info
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {}
    
    def get_process_list(self):
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes[:50]  # Limit to first 50 processes
        except Exception as e:
            logger.error(f"Error getting process list: {str(e)}")
            return []
    
    def format_command_output(self, output, command_type):
        """Format command output for better display"""
        if not output:
            return "No output"
        
        # Add command type context
        formatted_output = f"Command: {command_type}\n"
        formatted_output += "=" * 50 + "\n"
        formatted_output += output
        
        return formatted_output 