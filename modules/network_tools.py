import subprocess
import socket
import logging
import platform
from config import Config

logger = logging.getLogger(__name__)

class NetworkTools:
    """Network diagnostics and troubleshooting tools"""
    
    def __init__(self):
        """Initialize network tools"""
        self.os_type = platform.system().lower()
    
    def run_basic_diagnostics(self):
        """Run basic network diagnostics"""
        try:
            results = {
                'connectivity': self._test_internet_connectivity(),
                'dns': self._test_dns_resolution(),
                'local_network': self._test_local_network(),
                'network_interfaces': self._get_network_interfaces()
            }
            return results
        except Exception as e:
            logger.error(f"Error running network diagnostics: {str(e)}")
            return {'error': str(e)}
    
    def ping_host(self, hostname, count=4):
        """Ping a hostname and return results"""
        try:
            if self.os_type == 'windows':
                command = f'ping -n {count} {hostname}'
            else:
                command = f'ping -c {count} {hostname}'
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=Config.PING_TIMEOUT
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'Ping timed out after {Config.PING_TIMEOUT} seconds'
            }
        except Exception as e:
            logger.error(f"Error pinging {hostname}: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def nslookup(self, domain):
        """Perform DNS lookup for a domain"""
        try:
            command = f'nslookup {domain}'
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=Config.DNS_TIMEOUT
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': f'DNS lookup timed out after {Config.DNS_TIMEOUT} seconds'
            }
        except Exception as e:
            logger.error(f"Error performing nslookup for {domain}: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def get_network_config(self):
        """Get network configuration"""
        try:
            if self.os_type == 'windows':
                command = 'ipconfig /all'
            elif self.os_type == 'darwin':
                # Use macOS-specific commands for network config
                command = 'ifconfig && networksetup -listallnetworkservices'
            else:
                command = 'ifconfig'
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            logger.error(f"Error getting network config: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def get_macos_network_info(self):
        """Get detailed network information for macOS"""
        try:
            if self.os_type != 'darwin':
                return {'error': 'This method is only for macOS'}
            
            # Get WiFi information
            wifi_info = subprocess.run(
                '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Get network services
            network_services = subprocess.run(
                'networksetup -listallnetworkservices',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'wifi_info': wifi_info.stdout if wifi_info.returncode == 0 else 'Unable to get WiFi info',
                'network_services': network_services.stdout if network_services.returncode == 0 else 'Unable to get network services',
                'success': True
            }
        except Exception as e:
            logger.error(f"Error getting macOS network info: {str(e)}")
            return {'error': str(e)}
    
    def _test_internet_connectivity(self):
        """Test basic internet connectivity"""
        test_hosts = ['8.8.8.8', '1.1.1.1', 'google.com']
        results = {}
        
        for host in test_hosts:
            ping_result = self.ping_host(host, count=2)
            results[host] = ping_result
        
        return results
    
    def _test_dns_resolution(self):
        """Test DNS resolution"""
        test_domains = ['google.com', 'microsoft.com', 'apple.com']
        results = {}
        
        for domain in test_domains:
            nslookup_result = self.nslookup(domain)
            results[domain] = nslookup_result
        
        return results
    
    def _test_local_network(self):
        """Test local network connectivity"""
        try:
            # Get local IP
            local_ip = socket.gethostbyname(socket.gethostname())
            
            # Test gateway (assuming common gateway patterns)
            gateway_tests = []
            if self.os_type == 'windows':
                # Try to get default gateway
                try:
                    result = subprocess.run(
                        'route print | findstr "0.0.0.0"',
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if '0.0.0.0' in line:
                                parts = line.split()
                                if len(parts) >= 4:
                                    gateway = parts[3]
                                    gateway_tests.append(gateway)
                except Exception:
                    pass
            else:
                # For Unix-like systems
                try:
                    result = subprocess.run(
                        'route -n | grep "^0.0.0.0"',
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 2:
                                gateway = parts[1]
                                gateway_tests.append(gateway)
                except Exception:
                    pass
            
            # Test local network
            local_tests = {}
            for gateway in gateway_tests[:2]:  # Test up to 2 gateways
                ping_result = self.ping_host(gateway, count=2)
                local_tests[gateway] = ping_result
            
            return {
                'local_ip': local_ip,
                'gateway_tests': local_tests
            }
        except Exception as e:
            logger.error(f"Error testing local network: {str(e)}")
            return {'error': str(e)}
    
    def _get_network_interfaces(self):
        """Get network interface information"""
        try:
            if self.os_type == 'windows':
                command = 'ipconfig'
            elif self.os_type == 'darwin':
                # Use networksetup for macOS for better interface info
                command = 'networksetup -listallnetworkservices'
            else:
                command = 'ifconfig'
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            }
        except Exception as e:
            logger.error(f"Error getting network interfaces: {str(e)}")
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def format_network_results(self, results):
        """Format network diagnostic results for display"""
        if not results:
            return "No network diagnostic results available"
        
        formatted_output = "Network Diagnostics Results\n"
        formatted_output += "=" * 50 + "\n\n"
        
        # Internet connectivity
        if 'connectivity' in results:
            formatted_output += "Internet Connectivity:\n"
            for host, result in results['connectivity'].items():
                status = "✓" if result['success'] else "✗"
                formatted_output += f"  {status} {host}\n"
            formatted_output += "\n"
        
        # DNS resolution
        if 'dns' in results:
            formatted_output += "DNS Resolution:\n"
            for domain, result in results['dns'].items():
                status = "✓" if result['success'] else "✗"
                formatted_output += f"  {status} {domain}\n"
            formatted_output += "\n"
        
        # Local network
        if 'local_network' in results:
            local_net = results['local_network']
            if 'local_ip' in local_net:
                formatted_output += f"Local IP: {local_net['local_ip']}\n"
            if 'gateway_tests' in local_net:
                formatted_output += "Gateway Tests:\n"
                for gateway, result in local_net['gateway_tests'].items():
                    status = "✓" if result['success'] else "✗"
                    formatted_output += f"  {status} {gateway}\n"
            formatted_output += "\n"
        
        return formatted_output 