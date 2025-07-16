import platform
import logging
import subprocess

logger = logging.getLogger(__name__)

class OSDetector:
    """Detects and provides information about the operating system"""
    
    def __init__(self):
        """Initialize OS detector"""
        self.system = platform.system().lower()
        self.release = platform.release()
        self.version = platform.version()
    
    def detect_os(self):
        """Detect the operating system and return standardized name"""
        if self.system == 'windows':
            return 'Windows'
        elif self.system == 'darwin':
            return 'macOS'
        elif self.system == 'linux':
            return 'Linux'
        else:
            return 'Unknown'
    
    def get_os_details(self):
        """Get detailed OS information"""
        try:
            details = {
                'system': self.system,
                'release': self.release,
                'version': self.version,
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'node': platform.node()
            }
            
            # Get OS-specific details
            if self.system == 'windows':
                details.update(self._get_windows_details())
            elif self.system == 'darwin':
                details.update(self._get_macos_details())
            elif self.system == 'linux':
                details.update(self._get_linux_details())
            
            return details
        except Exception as e:
            logger.error(f"Error getting OS details: {str(e)}")
            return {'error': str(e)}
    
    def _get_windows_details(self):
        """Get Windows-specific details"""
        try:
            # Try to get Windows version info
            result = subprocess.run(
                ['systeminfo'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            details = {}
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'OS Name:' in line:
                        details['os_name'] = line.split(':', 1)[1].strip()
                    elif 'OS Version:' in line:
                        details['os_version'] = line.split(':', 1)[1].strip()
                    elif 'OS Manufacturer:' in line:
                        details['os_manufacturer'] = line.split(':', 1)[1].strip()
            
            return details
        except Exception as e:
            logger.error(f"Error getting Windows details: {str(e)}")
            return {}
    
    def _get_macos_details(self):
        """Get macOS-specific details"""
        try:
            # Get macOS version
            result = subprocess.run(
                ['sw_vers'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            details = {}
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'ProductName:' in line:
                        details['product_name'] = line.split(':', 1)[1].strip()
                    elif 'ProductVersion:' in line:
                        details['product_version'] = line.split(':', 1)[1].strip()
                    elif 'BuildVersion:' in line:
                        details['build_version'] = line.split(':', 1)[1].strip()
            
            return details
        except Exception as e:
            logger.error(f"Error getting macOS details: {str(e)}")
            return {}
    
    def _get_linux_details(self):
        """Get Linux-specific details"""
        try:
            details = {}
            
            # Try to read /etc/os-release
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            value = value.strip('"')
                            details[key.lower()] = value
            except FileNotFoundError:
                pass
            
            # Try to get kernel version
            try:
                result = subprocess.run(
                    ['uname', '-r'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    details['kernel_version'] = result.stdout.strip()
            except Exception:
                pass
            
            return details
        except Exception as e:
            logger.error(f"Error getting Linux details: {str(e)}")
            return {}
    
    def is_windows(self):
        """Check if running on Windows"""
        return self.system == 'windows'
    
    def is_macos(self):
        """Check if running on macOS"""
        return self.system == 'darwin'
    
    def is_linux(self):
        """Check if running on Linux"""
        return self.system == 'linux'
    
    def get_command_shell(self):
        """Get the appropriate command shell for the OS"""
        if self.system == 'windows':
            return 'cmd'
        else:
            return 'bash'
    
    def get_path_separator(self):
        """Get the path separator for the OS"""
        if self.system == 'windows':
            return '\\'
        else:
            return '/'
    
    def get_temp_directory(self):
        """Get the temporary directory for the OS"""
        import tempfile
        return tempfile.gettempdir() 