import openai
import logging
import uuid
from datetime import datetime
from config import Config
from modules.automated_diagnostics import AutomatedDiagnostics
from modules.chat_database import ChatDatabase
from modules.network_tools import NetworkTools

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles GPT-4o integration for intelligent IT support"""
    
    def __init__(self):
        """Initialize the chat handler with OpenAI configuration"""
        try:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.chat_database = ChatDatabase()
            self.automated_diagnostics = AutomatedDiagnostics()
            self.network_tools = NetworkTools()
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
            self.chat_database = ChatDatabase()
            self.automated_diagnostics = AutomatedDiagnostics()
            self.network_tools = NetworkTools()
    
    def process_message(self, user_message, os_type, session_id=None):
        """Process user message with GPT-4o for dynamic analysis and command generation"""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Create or update session
            self.chat_database.create_session(session_id, os_type)
            
            # Check internet connectivity first
            internet_available = self.network_tools.check_internet_connectivity()
            
            # Check if OpenAI client is available and internet is working
            if self.client is None or not internet_available:
                logger.warning("OpenAI client not available or no internet connection, using fallback response")
                fallback_response = self._get_fallback_response(user_message, os_type, internet_available)
                self.chat_database.store_message(
                    session_id, user_message, fallback_response, 
                    os_type, 'fallback'
                )
                return {
                    'response': fallback_response or '',
                    'system_commands': [],
                    'escalation': False
                }
            
            # Create dynamic system prompt for IT support
            system_prompt = self._create_dynamic_system_prompt(os_type)
            
            # Get conversation history for context (last 15 interactions)
            conversation = self._get_conversation_context(session_id, user_message)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            messages.extend(conversation)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                max_tokens=Config.OPENAI_MAX_TOKENS,
                temperature=Config.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            bot_response_text = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                import json
                parsed_response = json.loads(bot_response_text)
                
                # Extract components from JSON
                response_text = parsed_response.get('response', '')
                if not isinstance(response_text, str):
                    response_text = str(response_text) if response_text is not None else ''
                system_commands = parsed_response.get('system_commands', [])
                escalation = parsed_response.get('escalation', False)
                
                # Store in conversation history (store only the markdown response for chat history)
                self.chat_database.store_message(
                    session_id, user_message, response_text, 
                    os_type, 'gpt_analysis'
                )
                
                return {
                    'response': response_text or '',
                    'system_commands': system_commands,
                    'escalation': escalation
                }
                
            except json.JSONDecodeError as e:
                # If JSON parsing fails, use the original response
                logger.warning(f"Failed to parse JSON response from GPT-4o: {str(e)}")
                logger.warning(f"Raw response: {bot_response_text[:500]}...")
                self.chat_database.store_message(
                    session_id, user_message, bot_response_text, 
                    os_type, 'gpt_analysis'
                )
                return {
                    'response': bot_response_text or '',
                    'system_commands': [],
                    'escalation': False
                }
        except Exception as e:
            logger.error(f"Error processing message with GPT-4o: {str(e)}")
            fallback_response = self._get_fallback_response(user_message, os_type, False)
            if session_id:
                self.chat_database.store_message(
                    session_id, user_message, fallback_response, 
                    os_type, 'error'
                )
            return {
                'response': fallback_response or '',
                'system_commands': [],
                'escalation': False
            }
    
    def _create_dynamic_system_prompt(self, os_type):
        """Create dynamic system prompt for GPT-4o IT support"""
        return f"""You are an intelligent IT support assistant for {os_type}. Your role is to analyze PC problems and provide solutions.

**CRITICAL: You MUST respond in JSON format ONLY. NO OTHER TEXT ALLOWED.**

Your response must be a valid JSON object with this exact structure:

```json
{{
    "response": "Your conversational response to the user with explanations, step-by-step guidance, and any clarifying questions",
    "system_commands": [
        {{
            "command": "actual_command_to_run",
            "description": "What this command does and why it helps"
        }}
    ],
    "escalation": false
}}
```

**JSON RULES:**
- `response`: Your detailed response to the user (can include markdown formatting)
- `system_commands`: Array of commands that can be executed in {os_type} terminal/command prompt
- `escalation`: Set to `true` only if you cannot determine the issue and need human intervention
- Only include commands that are safe and can run in {os_type} terminal/command prompt
- If no commands are needed, use empty array: `"system_commands": []`
- ALWAYS wrap your entire response in the JSON format above
- NEVER include any text outside the JSON structure
- NEVER include any explanations about the JSON format in your response
- Your response must be parseable JSON only

**SUPPORT AREAS:**
- Hardware issues (peripherals, components, drivers)
- Software issues (applications, OS problems, performance)
- Network issues (connectivity, DNS, WiFi, Ethernet)
- System issues (disk space, processes, security)
- Peripheral issues (printers, audio, displays)

**OS-SPECIFIC COMMAND EXAMPLES:**

**Windows Commands:**
- `ping google.com -n 4` - Test internet connectivity
- `ipconfig /all` - View network configuration
- `systeminfo` - Get system information
- `tasklist /v` - List running processes
- `wmic logicaldisk get size,freespace,caption` - Check disk space
- `nslookup google.com` - Test DNS resolution
- `netstat -an` - Check network connections
- `sfc /scannow` - System file checker
- `chkdsk C:` - Check disk for errors
- `wmic printer list brief` - List printers
- `sc query spooler` - Check print spooler service
- `netsh wlan show profiles` - Show WiFi profiles
- `getmac /v` - Get MAC addresses
- `route print` - Show routing table

**macOS Commands:**
- `ping -c 4 google.com` - Test internet connectivity
- `ifconfig` - View network configuration
- `system_profiler SPHardwareDataType` - Get system information
- `ps aux --sort=-%cpu | head -20` - List top processes
- `df -h` - Check disk space
- `nslookup google.com` - Test DNS resolution
- `netstat -an` - Check network connections
- `diskutil list` - List disk information
- `sw_vers` - Get macOS version
- `system_profiler SPUSBDataType` - List USB devices
- `system_profiler SPAudioDataType` - List audio devices
- `system_profiler SPDisplaysDataType` - List display devices
- `networksetup -listallnetworkservices` - List network services
- `networksetup -getinfo Wi-Fi` - Get WiFi information
- `launchctl list | grep -i printer` - Check printer services
- `sudo dscacheutil -flushcache` - Flush DNS cache
- `sudo killall -HUP mDNSResponder` - Restart mDNS responder

**Linux Commands:**
- `ping -c 4 google.com` - Test internet connectivity
- `ifconfig` or `ip addr` - View network configuration
- `uname -a` - Get system information
- `ps aux --sort=-%cpu | head -20` - List top processes
- `df -h` - Check disk space
- `nslookup google.com` - Test DNS resolution
- `netstat -an` - Check network connections
- `lscpu` - CPU information
- `free -h` - Memory information
- `lspci` - List PCI devices
- `lsusb` - List USB devices
- `lshw` - List hardware
- `systemctl status` - Check system services
- `journalctl -f` - View system logs

**macOS SECURITY NOTES:**
- Some macOS commands require sudo privileges
- Commands like `system_profiler`, `diskutil`, `ioreg` may need password
- Network commands like `networksetup` may require admin privileges
- Always suggest non-privileged alternatives when possible
- If a command requires sudo, mention it in the description

**EXAMPLE RESPONSES:**

**Network Issue on Windows:**
```json
{{
    "response": "I understand you're having internet connectivity issues. Let me help you diagnose this step by step.\n\n**Step-by-Step Diagnosis:**\n1. First, let's test basic internet connectivity\n2. Check your network configuration\n3. Test DNS resolution\n4. Verify network connections\n\nI can run these diagnostic commands to help identify the issue:",
    "system_commands": [
        {{
            "command": "ping google.com -n 4",
            "description": "Test basic internet connectivity"
        }},
        {{
            "command": "ipconfig /all",
            "description": "View detailed network configuration"
        }},
        {{
            "command": "nslookup google.com",
            "description": "Test DNS resolution"
        }}
    ],
    "escalation": false
}}
```

**Network Issue on macOS:**
```json
{{
    "response": "I understand you're having internet connectivity issues on macOS. Let me help you diagnose this step by step.\n\n**Step-by-Step Diagnosis:**\n1. First, let's test basic internet connectivity\n2. Check your network configuration\n3. Test DNS resolution\n4. Verify network services\n\nI can run these diagnostic commands to help identify the issue:",
    "system_commands": [
        {{
            "command": "ping -c 4 google.com",
            "description": "Test basic internet connectivity"
        }},
        {{
            "command": "ifconfig",
            "description": "View network configuration"
        }},
        {{
            "command": "networksetup -listallnetworkservices",
            "description": "List all network services"
        }},
        {{
            "command": "nslookup google.com",
            "description": "Test DNS resolution"
        }}
    ],
    "escalation": false
}}
```

**Printer Issue on Windows:**
```json
{{
    "response": "I understand you're having printer problems on Windows. Let me help you troubleshoot this.\n\n**Step-by-Step Diagnosis:**\n1. Check if printer is recognized by the system\n2. Verify print spooler service\n3. Test basic printing functionality\n\nI can run these diagnostic commands to help identify the issue:",
    "system_commands": [
        {{
            "command": "wmic printer list brief",
            "description": "Check if printer is recognized by Windows"
        }},
        {{
            "command": "sc query spooler",
            "description": "Check print spooler service status"
        }}
    ],
    "escalation": false
}}
```

**Printer Issue on macOS:**
```json
{{
    "response": "I understand you're having printer problems on macOS. Let me help you troubleshoot this.\n\n**Step-by-Step Diagnosis:**\n1. Check if printer is recognized by the system\n2. Verify print services\n3. Test basic printing functionality\n\nI can run these diagnostic commands to help identify the issue:",
    "system_commands": [
        {{
            "command": "system_profiler SPUSBDataType",
            "description": "Check USB devices including printers"
        }},
        {{
            "command": "launchctl list | grep -i printer",
            "description": "Check printer services"
        }},
        {{
            "command": "lpstat -p",
            "description": "List available printers"
        }}
    ],
    "escalation": false
}}
```

**Escalation Case:**
```json
{{
    "response": "I'm not entirely sure about the specific issue you're describing. This may require escalation to an IT technician who can provide more specialized assistance.\n\n**Escalation Reason:**\nThe issue you're experiencing involves complex hardware diagnostics that require physical inspection or specialized tools that aren't available through remote commands.\n\n**Next Steps:**\nPlease contact your IT support team for assistance with this issue.",
    "system_commands": [],
    "escalation": true
}}
```

**Remember:**
- ALWAYS respond in the exact JSON format above
- NEVER include any text outside the JSON structure
- Only include commands that can run in {os_type} terminal/command prompt
- Make commands safe and non-destructive
- Escalate only when you truly cannot determine the issue
- Provide clear explanations in the response field
- For macOS, mention if commands require sudo privileges
- Always suggest OS-specific commands based on the user's operating system"""
    
    def _get_conversation_context(self, session_id, current_message):
        """Get recent conversation history for context"""
        # Fetch last 15 interactions for context
        interactions = self.chat_database.get_conversation_history(session_id, limit=15)
        messages = []
        for interaction in interactions:
            messages.append({"role": "user", "content": interaction['user_message']})
            messages.append({"role": "assistant", "content": interaction['bot_response']})
        return messages
    
    def _get_fallback_response(self, user_message, os_type, internet_available=True):
        """Provide fallback response when GPT-4o is unavailable"""
        if not internet_available:
            # Get network-specific fallback commands
            fallback_data = self.network_tools.get_network_fallback_commands(os_type)
            
            response = f"""**🌐 No Internet Connection Detected**

I notice you don't have an internet connection, which is preventing me from using my AI capabilities. However, I can still help you troubleshoot your network issues with these diagnostic commands:

**🔧 Network Diagnostic Commands for {os_type}:**

"""
            
            # Add diagnostic commands with proper HTML formatting
            for cmd in fallback_data['diagnostic_commands']:
                # Check if command requires sudo on macOS
                requires_sudo = False
                if os_type.lower() in ['darwin', 'macos', 'mac']:
                    sudo_commands = ['sudo', 'system_profiler', 'diskutil', 'ioreg', 'launchctl', 
                                   'dscacheutil', 'killall', 'repair_packages', 'log show']
                    requires_sudo = any(sudo_cmd in cmd['command'].lower() for sudo_cmd in sudo_commands)
                
                if requires_sudo:
                    # For macOS commands that require sudo, add password prompt
                    response += f"""<div class="command-container">
    <code>{cmd['command']}</code>
    <div class="command-description">{cmd['description']} (requires password)</div>
    <div class="password-prompt" style="display: none;">
        <input type="password" class="form-control form-control-sm" placeholder="Enter your password" style="width: 200px; margin: 4px 0;">
        <button class="btn btn-sm btn-primary" onclick="executeCommandWithPasswordFromFallback('{cmd['command']}', this)">
            <i class="fas fa-key me-1"></i>Run with Password
        </button>
        <button class="btn btn-sm btn-secondary" onclick="cancelPasswordPrompt(this)">
            <i class="fas fa-times me-1"></i>Cancel
        </button>
    </div>
    <button class="btn btn-sm btn-outline-warning run-command-btn" onclick="showPasswordPrompt(this)">
        <i class="fas fa-lock me-1"></i>Run (Sudo)
    </button>
</div>
"""
                else:
                    # For regular commands, use normal run button
                    response += f"""<div class="command-container">
    <code>{cmd['command']}</code>
    <button class="btn btn-sm btn-outline-primary run-command-btn" onclick="executeCommand('{cmd['command']}')">
        <i class="fas fa-play me-1"></i>Run
    </button>
    <div class="command-description">{cmd['description']}</div>
</div>
"""
            
            response += f"""

**📋 Troubleshooting Steps:**
<ul>
"""
            for step in fallback_data['troubleshooting_steps']:
                response += f"<li>{step}</li>\n"
            
            response += f"""</ul>

**💡 How to use:**
1. Click the 'Run' button next to any command above
2. For commands marked with (Sudo), you'll be prompted for your password
3. Review the output to identify the issue
4. Follow the troubleshooting steps
5. Try the commands again to verify the fix

**Your Message:** {user_message}
**Operating System:** {os_type}
**Status:** No internet connection detected"""
            
            return response
        else:
            return f"""**🤖 System Temporarily Unavailable**

I'm having trouble processing your request right now. Here are some general troubleshooting steps you can try:

**🔧 General Troubleshooting:**
1. Restart your computer
2. Check if the issue persists after restart
3. Try the same action in a different application
4. Check for system updates

**📞 Support:**
If the issue continues, please contact IT support for assistance.

**Your Message:** {user_message}
**Operating System:** {os_type}"""
    
    def _create_enhanced_response(self, response_text, system_commands, escalation):
        """Create enhanced response with command buttons and escalation handling"""
        enhanced_response = response_text
        
        # Add command buttons if there are system commands
        if system_commands and not escalation:
            enhanced_response += "\n\n**🔧 Available Commands:**\n"
            for i, cmd in enumerate(system_commands):
                command = cmd.get('command', '')
                description = cmd.get('description', '')
                enhanced_response += f"\n• `{command}` - {description}"
            enhanced_response += "\n\n*Click the 'Run' button next to any command to execute it.*"
            
            # Store commands in database for frontend access
            self._store_commands_for_session(system_commands)
        
        # Add escalation message if needed
        if escalation:
            enhanced_response += "\n\n**⚠️ Escalation Required:**\nThis issue requires escalation to a human IT technician. Please contact your IT support team for assistance."
        
        return enhanced_response
    
    def _store_commands_for_session(self, system_commands):
        """Store commands in database for frontend access"""
        try:
            # Store commands in a way that frontend can access them
            # This could be in session storage or a separate table
            for cmd in system_commands:
                command = cmd.get('command', '')
                description = cmd.get('description', '')
                # You could store this in the database if needed
                logger.info(f"Command available: {command} - {description}")
        except Exception as e:
            logger.error(f"Error storing commands: {str(e)}") 