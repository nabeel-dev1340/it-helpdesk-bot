import subprocess
import platform
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DiagnosticCommand:
    """Represents a diagnostic command that can be executed"""
    name: str
    description: str
    command: str
    category: str
    risk_level: str  # 'low', 'medium', 'high'
    requires_permission: bool = True

class AutomatedDiagnostics:
    """Handles automated diagnostics and command execution"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.diagnostic_commands = self._initialize_commands()
    
    def _initialize_commands(self) -> Dict[str, List[DiagnosticCommand]]:
        """Initialize OS-specific diagnostic commands"""
        commands = {
            'network': [],
            'system': [],
            'storage': [],
            'security': [],
            'performance': []
        }
        
        if self.os_type == 'windows':
            commands['network'].extend([
                DiagnosticCommand(
                    name="Network Configuration",
                    description="Check current network settings and IP configuration",
                    command="ipconfig /all",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="DNS Resolution Test",
                    description="Test DNS resolution for common domains",
                    command="nslookup google.com",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Network Connectivity Test",
                    description="Test connectivity to multiple servers",
                    command="ping -n 4 google.com",
                    category="network",
                    risk_level="low"
                )
            ])
            
            commands['system'].extend([
                DiagnosticCommand(
                    name="System Information",
                    description="Get detailed system information",
                    command="systeminfo",
                    category="system",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Running Processes",
                    description="List currently running processes",
                    command="tasklist",
                    category="system",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="System Health Check",
                    description="Check system file integrity",
                    command="sfc /scannow",
                    category="system",
                    risk_level="medium"
                )
            ])
            
            commands['storage'].extend([
                DiagnosticCommand(
                    name="Disk Space Analysis",
                    description="Check disk space usage",
                    command="wmic logicaldisk get size,freespace,caption",
                    category="storage",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Disk Health Check",
                    description="Check disk for errors",
                    command="chkdsk C: /f",
                    category="storage",
                    risk_level="high"
                )
            ])
            
        elif self.os_type == 'darwin':  # macOS
            commands['network'].extend([
                DiagnosticCommand(
                    name="Network Configuration",
                    description="Check current network settings",
                    command="ifconfig",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="DNS Resolution Test",
                    description="Test DNS resolution",
                    command="nslookup google.com",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Network Connectivity Test",
                    description="Test connectivity to servers",
                    command="ping -c 4 google.com",
                    category="network",
                    risk_level="low"
                )
            ])
            
            commands['system'].extend([
                DiagnosticCommand(
                    name="System Information",
                    description="Get system hardware information",
                    command="system_profiler SPHardwareDataType",
                    category="system",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Running Processes",
                    description="List running processes",
                    command="ps aux --sort=-%cpu | head -20",
                    category="system",
                    risk_level="low"
                )
            ])
            
            commands['storage'].extend([
                DiagnosticCommand(
                    name="Disk Space Analysis",
                    description="Check disk space usage",
                    command="df -h",
                    category="storage",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Disk Health Check",
                    description="Check disk for errors",
                    command="diskutil verifyDisk /",
                    category="storage",
                    risk_level="medium"
                )
            ])
            
        else:  # Linux
            commands['network'].extend([
                DiagnosticCommand(
                    name="Network Configuration",
                    description="Check network interfaces",
                    command="ip addr show",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="DNS Resolution Test",
                    description="Test DNS resolution",
                    command="nslookup google.com",
                    category="network",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Network Connectivity Test",
                    description="Test connectivity",
                    command="ping -c 4 google.com",
                    category="network",
                    risk_level="low"
                )
            ])
            
            commands['system'].extend([
                DiagnosticCommand(
                    name="System Information",
                    description="Get system information",
                    command="uname -a && cat /etc/os-release",
                    category="system",
                    risk_level="low"
                ),
                DiagnosticCommand(
                    name="Running Processes",
                    description="List running processes",
                    command="ps aux --sort=-%cpu | head -20",
                    category="system",
                    risk_level="low"
                )
            ])
            
            commands['storage'].extend([
                DiagnosticCommand(
                    name="Disk Space Analysis",
                    description="Check disk space usage",
                    command="df -h",
                    category="storage",
                    risk_level="low"
                )
            ])
        
        return commands
    
    def get_suggested_diagnostics(self, issue_category: str) -> List[DiagnosticCommand]:
        """Get suggested diagnostics based on issue category"""
        suggestions = []
        
        if issue_category == 'network':
            suggestions.extend(self.diagnostic_commands['network'])
        elif issue_category == 'performance':
            suggestions.extend(self.diagnostic_commands['system'])
            suggestions.extend(self.diagnostic_commands['storage'])
        elif issue_category == 'storage':
            suggestions.extend(self.diagnostic_commands['storage'])
        elif issue_category == 'system':
            suggestions.extend(self.diagnostic_commands['system'])
        else:
            # General diagnostics
            suggestions.extend(self.diagnostic_commands['system'][:2])  # First 2 system commands
            suggestions.extend(self.diagnostic_commands['network'][:1])  # First network command
        
        return suggestions
    
    def execute_command(self, command: DiagnosticCommand) -> Tuple[bool, str]:
        """Execute a diagnostic command safely"""
        try:
            logger.info(f"Executing command: {command.command}")
            
            # Execute the command
            result = subprocess.run(
                command.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or "Command failed with no error output"
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            logger.error(f"Error executing command {command.command}: {str(e)}")
            return False, f"Error executing command: {str(e)}"
    
    def format_diagnostic_suggestions(self, suggestions: List[DiagnosticCommand]) -> str:
        """Format diagnostic suggestions for display"""
        if not suggestions:
            return ""
        
        formatted = "**🔍 Suggested Diagnostics:**\n\n"
        
        for cmd in suggestions:
            risk_emoji = "🟢" if cmd.risk_level == "low" else "🟡" if cmd.risk_level == "medium" else "🔴"
            formatted += f"• **{cmd.name}** {risk_emoji} - {cmd.description}\n"
        
        formatted += "\n**Would you like me to run these diagnostics automatically?** (I'll ask for permission before each command)"
        
        return formatted
    
    def categorize_user_issue(self, user_message: str) -> str:
        """Categorize user issue for appropriate diagnostics"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['internet', 'wifi', 'network', 'connection', 'ping', 'dns']):
            return 'network'
        elif any(word in message_lower for word in ['slow', 'freeze', 'crash', 'performance', 'lag']):
            return 'performance'
        elif any(word in message_lower for word in ['disk', 'storage', 'space', 'full', 'memory']):
            return 'storage'
        elif any(word in message_lower for word in ['error', 'blue screen', 'kernel', 'system']):
            return 'system'
        else:
            return 'general' 