import openai
import logging
import uuid
from datetime import datetime
from config import Config
from modules.automated_diagnostics import AutomatedDiagnostics
from modules.chat_database import ChatDatabase

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles GPT-4o integration for intelligent IT support"""
    
    def __init__(self):
        """Initialize the chat handler with OpenAI configuration"""
        try:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.chat_database = ChatDatabase()
            self.automated_diagnostics = AutomatedDiagnostics()
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
            self.chat_database = ChatDatabase()
            self.automated_diagnostics = AutomatedDiagnostics()
    
    def process_message(self, user_message, os_type, session_id=None):
        """Process user message with GPT-4o for dynamic analysis and command generation"""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Create or update session
            self.chat_database.create_session(session_id, os_type)
            
            # Check if OpenAI client is available
            if self.client is None:
                logger.warning("OpenAI client not available, using fallback response")
                fallback_response = self._get_fallback_response(user_message, os_type)
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
            fallback_response = self._get_fallback_response(user_message, os_type)
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

**COMMAND EXAMPLES FOR {os_type}:**

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

**EXAMPLE RESPONSES:**

**Network Issue:**
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

**Printer Issue:**
```json
{{
    "response": "I understand you're having printer problems. Let me help you troubleshoot this.\n\n**Step-by-Step Diagnosis:**\n1. Check if printer is recognized by the system\n2. Verify print spooler service\n3. Test basic printing functionality\n\nI can run these diagnostic commands to help identify the issue:",
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
- Provide clear explanations in the response field"""
    
    def _get_conversation_context(self, session_id, current_message):
        """Get recent conversation history for context"""
        # Fetch last 15 interactions for context
        interactions = self.chat_database.get_conversation_history(session_id, limit=15)
        messages = []
        for interaction in interactions:
            messages.append({"role": "user", "content": interaction['user_message']})
            messages.append({"role": "assistant", "content": interaction['bot_response']})
        return messages
    
    def _get_fallback_response(self, user_message, os_type):
        """Provide fallback response when GPT-4o is unavailable"""
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