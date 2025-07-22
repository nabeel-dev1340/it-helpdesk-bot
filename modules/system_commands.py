import subprocess
import platform
import logging
import psutil
import time
import getpass
import os
from config import Config

logger = logging.getLogger(__name__)

class SystemCommands:
    """Handles safe execution of system commands"""
    
    def __init__(self):
        """Initialize system commands handler"""
        self.os_type = platform.system().lower()
        self.command_cache = {}  # Simple cache for quick commands
        self.cache_timeout = 30  # Cache for 30 seconds
        self.sudo_password = None  # Store sudo password for macOS
    
    def set_sudo_password(self, password):
        """Set sudo password for macOS commands"""
        self.sudo_password = password
        logger.info("Sudo password set for macOS commands")
    
    def execute_command(self, command, require_sudo=False):
        """Execute a system command safely with optimized timeouts"""
        try:
            # Check cache first for quick commands
            cache_key = f"{command}_{self.os_type}_{require_sudo}"
            if cache_key in self.command_cache:
                cache_entry = self.command_cache[cache_key]
                if time.time() - cache_entry['timestamp'] < self.cache_timeout:
                    logger.info(f"Using cached result for command: {command}")
                    return cache_entry['result']
            
            # Validate command before execution
            if not self._is_command_safe(command):
                return {
                    'success': False,
                    'output': 'Command not allowed for security reasons',
                    'error': 'Security validation failed'
                }
            
            # Handle macOS sudo commands
            if self.os_type == 'darwin' and require_sudo:
                if not self.sudo_password:
                    return {
                        'success': False,
                        'output': '',
                        'error': 'Sudo password required for this command. Please provide your password.',
                        'requires_password': True
                    }
                # Prepend sudo to command
                command = f"echo '{self.sudo_password}' | sudo -S {command}"
            
            # Determine timeout based on command type
            timeout = self._get_command_timeout(command)
            
            # Execute command with optimized timeout
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Truncate output if too long
            output = result.stdout
            if len(output) > Config.MAX_COMMAND_OUTPUT:
                output = output[:Config.MAX_COMMAND_OUTPUT] + "\n... (output truncated)"
            
            result_data = {
                'success': result.returncode == 0,
                'output': output,
                'error': result.stderr if result.stderr else None,
                'return_code': result.returncode,
                'execution_time': time.time()
            }
            
            # Cache quick commands
            if self._is_quick_command(command):
                self.command_cache[cache_key] = {
                    'result': result_data,
                    'timestamp': time.time()
                }
            
            return result_data
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            logger.error(f"Error executing command '{command}': {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': f'Command execution failed: {str(e)}'
            }
    
    def _get_command_timeout(self, command):
        """Get appropriate timeout for command type"""
        command_lower = command.lower()
        
        # Quick commands - fast timeout
        if any(cmd in command_lower for cmd in ['ping', 'nslookup', 'ipconfig', 'ifconfig', 'echo']):
            return Config.QUICK_COMMAND_TIMEOUT
        
        # Medium commands - moderate timeout
        if any(cmd in command_lower for cmd in ['tasklist', 'ps', 'df', 'free', 'uname']):
            return Config.MEDIUM_COMMAND_TIMEOUT
        
        # Slow commands - longer timeout
        if any(cmd in command_lower for cmd in ['systeminfo', 'system_profiler', 'sfc', 'chkdsk']):
            return Config.SLOW_COMMAND_TIMEOUT
        
        # macOS-specific slow commands
        if self.os_type == 'darwin' and any(cmd in command_lower for cmd in ['system_profiler', 'diskutil', 'ioreg']):
            return Config.SLOW_COMMAND_TIMEOUT
        
        # Default timeout
        return Config.COMMAND_TIMEOUT
    
    def clear_cache(self):
        """Clear the command cache"""
        self.command_cache.clear()
        logger.info("Command cache cleared")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0
        
        for cache_entry in self.command_cache.values():
            if current_time - cache_entry['timestamp'] < self.cache_timeout:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.command_cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_timeout': self.cache_timeout
        }
    
    def _is_quick_command(self, command):
        """Check if command is suitable for caching"""
        command_lower = command.lower()
        quick_commands = ['ping', 'nslookup', 'ipconfig', 'ifconfig', 'echo', 'uname', 'df']
        
        # Add macOS-specific quick commands
        if self.os_type == 'darwin':
            quick_commands.extend(['hostname', 'whoami', 'pwd', 'sw_vers'])
        
        return any(cmd in command_lower for cmd in quick_commands)
    
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
        """Validate if command is safe to execute"""
        command_lower = command.lower()
        
        # Check for blocked patterns
        for pattern in Config.BLOCKED_PATTERNS:
            if pattern in command_lower:
                logger.warning(f"Blocked command pattern detected: {pattern}")
                return False
        
        # Check OS-specific allowed commands
        if self.os_type == 'windows':
            allowed_commands = Config.WINDOWS_COMMANDS
        elif self.os_type == 'darwin':
            allowed_commands = Config.MACOS_COMMANDS
        else:
            allowed_commands = Config.LINUX_COMMANDS
        
        # Check if command starts with an allowed command
        for allowed_cmd in allowed_commands:
            if command_lower.startswith(allowed_cmd):
                return True
        
        logger.warning(f"Command not in allowed list: {command}")
        return False
    
    def _requires_sudo(self, command):
        """Check if command requires sudo on macOS"""
        if self.os_type != 'darwin':
            return False
        
        command_lower = command.lower()
        sudo_commands = [
            'sudo', 'system_profiler', 'diskutil', 'ioreg', 'launchctl',
            'dscacheutil', 'killall', 'repair_packages', 'log show'
        ]
        
        return any(cmd in command_lower for cmd in sudo_commands)
    
    def get_network_info(self):
        """Get network information"""
        try:
            network_info = {}
            
            # Get network interfaces
            if self.os_type == 'windows':
                result = subprocess.run('ipconfig', shell=True, capture_output=True, text=True, timeout=10)
                network_info['interfaces'] = result.stdout
            else:
                result = subprocess.run('ifconfig', shell=True, capture_output=True, text=True, timeout=10)
                network_info['interfaces'] = result.stdout
            
            # Get routing table
            try:
                if self.os_type == 'windows':
                    route_result = subprocess.run('route print', shell=True, capture_output=True, text=True, timeout=10)
                else:
                    route_result = subprocess.run('netstat -rn', shell=True, capture_output=True, text=True, timeout=10)
                network_info['routing'] = route_result.stdout
            except:
                network_info['routing'] = "Unable to get routing information"
            
            return network_info
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {'error': str(e)}
    
    def get_process_list(self):
        """Get list of running processes"""
        try:
            if self.os_type == 'windows':
                result = subprocess.run('tasklist /v', shell=True, capture_output=True, text=True, timeout=15)
            else:
                result = subprocess.run('ps aux --sort=-%cpu | head -20', shell=True, capture_output=True, text=True, timeout=15)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            logger.error(f"Error getting process list: {str(e)}")
            return {'error': str(e)}
    
    def format_command_output(self, output, command_type):
        """Format command output for better display"""
        if not output:
            return "No output available"
        
        # Truncate very long outputs
        if len(output) > 2000:
            output = output[:2000] + "\n... (output truncated for display)"
        
        return output 