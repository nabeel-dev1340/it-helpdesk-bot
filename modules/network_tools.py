import subprocess
import platform
import logging
import socket
import requests
from config import Config

logger = logging.getLogger(__name__)

class NetworkTools:
    """Network diagnostic and testing tools"""
    
    def __init__(self):
        """Initialize network tools"""
        self.os_type = platform.system().lower()
    
    def check_internet_connectivity(self):
        """Check if internet is available"""
        try:
            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            pass
        
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.4.4", 53), timeout=3)
            return True
        except OSError:
            pass
        
        try:
            # Try to connect to Cloudflare DNS
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            return True
        except OSError:
            pass
        
        return False
    
    def check_dns_resolution(self):
        """Check if DNS resolution is working"""
        try:
            # Try to resolve a domain
            socket.gethostbyname("google.com")
            return True
        except socket.gaierror:
            return False
    
    def get_network_fallback_commands(self, os_type):
        """Get fallback commands for network issues based on OS"""
        if os_type.lower() in ['windows', 'win']:
            return {
                'diagnostic_commands': [
                    {
                        'command': 'ipconfig /all',
                        'description': 'View detailed network configuration',
                        'category': 'network_config'
                    },
                    {
                        'command': 'ping google.com -n 4',
                        'description': 'Test internet connectivity',
                        'category': 'connectivity'
                    },
                    {
                        'command': 'nslookup google.com',
                        'description': 'Test DNS resolution',
                        'category': 'dns'
                    },
                    {
                        'command': 'netstat -an',
                        'description': 'Check active network connections',
                        'category': 'connections'
                    },
                    {
                        'command': 'route print',
                        'description': 'View routing table',
                        'category': 'routing'
                    },
                    {
                        'command': 'netsh wlan show profiles',
                        'description': 'Show WiFi profiles',
                        'category': 'wifi'
                    },
                    {
                        'command': 'netsh interface show interface',
                        'description': 'Show network interfaces',
                        'category': 'interfaces'
                    }
                ],
                'troubleshooting_steps': [
                    '1. Check if your network cable is properly connected',
                    '2. Try restarting your router/modem',
                    '3. Check if other devices can connect to the internet',
                    '4. Try connecting to a different network',
                    '5. Contact your ISP if the issue persists'
                ]
            }
        elif os_type.lower() in ['darwin', 'macos', 'mac']:
            return {
                'diagnostic_commands': [
                    {
                        'command': 'ifconfig',
                        'description': 'View network configuration',
                        'category': 'network_config'
                    },
                    {
                        'command': 'ping -c 4 google.com',
                        'description': 'Test internet connectivity',
                        'category': 'connectivity'
                    },
                    {
                        'command': 'nslookup google.com',
                        'description': 'Test DNS resolution',
                        'category': 'dns'
                    },
                    {
                        'command': 'netstat -an',
                        'description': 'Check active network connections',
                        'category': 'connections'
                    },
                    {
                        'command': 'networksetup -listallnetworkservices',
                        'description': 'List all network services',
                        'category': 'services'
                    },
                    {
                        'command': 'networksetup -getinfo Wi-Fi',
                        'description': 'Get WiFi information',
                        'category': 'wifi'
                    },
                    {
                        'command': 'sudo dscacheutil -flushcache',
                        'description': 'Flush DNS cache (requires password)',
                        'category': 'dns_cache'
                    },
                    {
                        'command': 'sudo killall -HUP mDNSResponder',
                        'description': 'Restart mDNS responder (requires password)',
                        'category': 'dns_service'
                    },
                    {
                        'command': 'sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4',
                        'description': 'Set DNS servers to Google (requires password)',
                        'category': 'dns_config'
                    },
                    {
                        'command': 'sudo ifconfig en0 down && sudo ifconfig en0 up',
                        'description': 'Restart WiFi interface (requires password)',
                        'category': 'interface_reset'
                    },
                    {
                        'command': 'sudo system_profiler SPNetworkDataType',
                        'description': 'Get detailed network information (requires password)',
                        'category': 'network_info'
                    },
                    {
                        'command': 'sudo launchctl unload /System/Library/LaunchDaemons/com.apple.mDNSResponder.plist',
                        'description': 'Unload mDNS responder service (requires password)',
                        'category': 'service_management'
                    },
                    {
                        'command': 'sudo launchctl load /System/Library/LaunchDaemons/com.apple.mDNSResponder.plist',
                        'description': 'Load mDNS responder service (requires password)',
                        'category': 'service_management'
                    }
                ],
                'troubleshooting_steps': [
                    '1. Check if your network cable is properly connected',
                    '2. Try restarting your router/modem',
                    '3. Check if other devices can connect to the internet',
                    '4. Try connecting to a different network',
                    '5. Reset network settings if needed',
                    '6. Contact your ISP if the issue persists'
                ]
            }
        else:  # Linux
            return {
                'diagnostic_commands': [
                    {
                        'command': 'ifconfig',
                        'description': 'View network configuration',
                        'category': 'network_config'
                    },
                    {
                        'command': 'ping -c 4 google.com',
                        'description': 'Test internet connectivity',
                        'category': 'connectivity'
                    },
                    {
                        'command': 'nslookup google.com',
                        'description': 'Test DNS resolution',
                        'category': 'dns'
                    },
                    {
                        'command': 'netstat -an',
                        'description': 'Check active network connections',
                        'category': 'connections'
                    },
                    {
                        'command': 'ip addr',
                        'description': 'View IP addresses',
                        'category': 'ip_config'
                    },
                    {
                        'command': 'ip route',
                        'description': 'View routing table',
                        'category': 'routing'
                    },
                    {
                        'command': 'systemctl status NetworkManager',
                        'description': 'Check NetworkManager status',
                        'category': 'network_manager'
                    }
                ],
                'troubleshooting_steps': [
                    '1. Check if your network cable is properly connected',
                    '2. Try restarting your router/modem',
                    '3. Check if other devices can connect to the internet',
                    '4. Try connecting to a different network',
                    '5. Restart network services if needed',
                    '6. Contact your ISP if the issue persists'
                ]
            }
    
    def run_basic_diagnostics(self):
        """Run basic network diagnostics"""
        try:
            results = {
                'connectivity': {},
                'dns': {},
                'interfaces': {}
            }
            
            # Test connectivity to common hosts
            hosts = ['google.com', 'cloudflare.com', '1.1.1.1']
            for host in hosts:
                try:
                    if self.os_type == 'windows':
                        result = subprocess.run(f'ping {host} -n 1', shell=True, capture_output=True, text=True, timeout=5)
                    else:
                        result = subprocess.run(f'ping -c 1 {host}', shell=True, capture_output=True, text=True, timeout=5)
                    
                    results['connectivity'][host] = {
                        'success': result.returncode == 0,
                        'output': result.stdout
                    }
                except Exception as e:
                    results['connectivity'][host] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Test DNS resolution
            domains = ['google.com', 'cloudflare.com']
            for domain in domains:
                try:
                    result = subprocess.run(f'nslookup {domain}', shell=True, capture_output=True, text=True, timeout=5)
                    results['dns'][domain] = {
                        'success': result.returncode == 0,
                        'output': result.stdout
                    }
                except Exception as e:
                    results['dns'][domain] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Get network interfaces
            try:
                if self.os_type == 'windows':
                    result = subprocess.run('ipconfig', shell=True, capture_output=True, text=True, timeout=10)
                else:
                    result = subprocess.run('ifconfig', shell=True, capture_output=True, text=True, timeout=10)
                
                results['interfaces'] = {
                    'success': result.returncode == 0,
                    'output': result.stdout
                }
            except Exception as e:
                results['interfaces'] = {
                    'success': False,
                    'error': str(e)
                }
            
            return results
        except Exception as e:
            logger.error(f"Error running network diagnostics: {str(e)}")
            return {'error': str(e)}
    
    def get_macos_network_info(self):
        """Get macOS-specific network information"""
        try:
            results = {}
            
            # Get WiFi information
            try:
                result = subprocess.run('networksetup -getinfo Wi-Fi', shell=True, capture_output=True, text=True, timeout=10)
                results['wifi_info'] = result.stdout if result.returncode == 0 else "Unable to get WiFi information"
            except Exception as e:
                results['wifi_info'] = f"Error getting WiFi info: {str(e)}"
            
            # Get network services
            try:
                result = subprocess.run('networksetup -listallnetworkservices', shell=True, capture_output=True, text=True, timeout=10)
                results['network_services'] = result.stdout if result.returncode == 0 else "Unable to get network services"
            except Exception as e:
                results['network_services'] = f"Error getting network services: {str(e)}"
            
            return results
        except Exception as e:
            logger.error(f"Error getting macOS network info: {str(e)}")
            return {'error': str(e)} 