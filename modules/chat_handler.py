import openai
import logging
from config import Config
from modules.automated_diagnostics import AutomatedDiagnostics

logger = logging.getLogger(__name__)

class ChatHandler:
    """Handles GPT-4o integration for intelligent IT support"""
    
    def __init__(self):
        """Initialize the chat handler with OpenAI configuration"""
        try:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.conversation_history = {}
            self.automated_diagnostics = AutomatedDiagnostics()
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
            self.conversation_history = {}
            self.automated_diagnostics = AutomatedDiagnostics()
        
    def process_message(self, user_message, os_type):
        """Process user message with GPT-4o and return intelligent response"""
        try:
            # Check if OpenAI client is available
            if self.client is None:
                logger.warning("OpenAI client not available, using fallback response")
                return self._get_fallback_response(user_message, os_type)
            
            # Create system prompt for IT support
            system_prompt = self._create_system_prompt(os_type)
            
            # Get conversation history for context
            conversation = self._get_conversation_context(user_message)
            
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
                temperature=Config.OPENAI_TEMPERATURE
            )
            
            bot_response = response.choices[0].message.content
            
            # Add diagnostic suggestions if appropriate
            bot_response = self._add_diagnostic_suggestions(bot_response, user_message)
            
            # Store in conversation history
            self._update_conversation_history(user_message, bot_response)
            
            return bot_response
            
        except Exception as e:
            logger.error(f"Error processing message with GPT-4o: {str(e)}")
            return self._get_fallback_response(user_message, os_type)
    
    def _create_system_prompt(self, os_type):
        """Create system prompt for IT support based on OS"""
        base_prompt = f"""You are an intelligent IT support assistant. The user is on {os_type}.

Your role is to:
1. Understand IT issues described in natural language
2. Provide step-by-step troubleshooting guidance
3. Suggest appropriate system commands for {os_type}
4. Ask clarifying questions when needed
5. Maintain a helpful and professional tone
6. Proactively suggest automated diagnostics when appropriate

IMPORTANT: Format your responses beautifully using markdown:
- Use **bold** for important points and section headers
- Use bullet points (•) for lists
- Use numbered lists for step-by-step instructions
- Use `code blocks` for commands and file paths
- Use emojis sparingly to make responses friendly
- Structure responses with clear sections
- Use proper spacing for readability

AUTOMATED DIAGNOSTICS:
When you identify a problem that can be diagnosed automatically, suggest running diagnostics with this format:

**🔍 Suggested Diagnostics:**
• **Network Test** - I can run ping tests and DNS checks
• **System Health Check** - I can check running processes and system resources
• **Disk Space Analysis** - I can analyze storage usage
• **Network Configuration** - I can check network settings

**Would you like me to run these diagnostics automatically?** (I'll ask for permission before each command)

For {os_type}, you can suggest these diagnostic commands:
- Network: ipconfig/ifconfig, ping, nslookup, netstat
- System: systeminfo/system_profiler, tasklist/ps, sfc/diskutil
- Security: chkdsk, system file checks

Always explain what commands do before suggesting them. If a command might be risky, warn the user first.

Keep responses concise but informative. If you need more information, ask specific questions.

Example response format:
**🔧 Network Issue Diagnosis**

I can help you troubleshoot your network connection! Here's what we can do:

**Quick Actions:**
• Network Test - Check connectivity
• Ping Test - Test internet access
• DNS Lookup - Verify DNS resolution

**🔍 Suggested Diagnostics:**
• **Network Connectivity Test** - I can run ping tests to google.com and other servers
• **DNS Resolution Check** - I can test DNS resolution for common domains
• **Network Configuration** - I can check your current network settings

**Would you like me to run these diagnostics automatically?** (I'll ask for permission before each command)

**Step-by-Step Process:**
1. First, let's check your network configuration
2. Then test basic connectivity
3. Finally, diagnose any issues found

Would you like me to run any of these diagnostics for you?"""
        
        return base_prompt
    
    def _get_conversation_context(self, current_message):
        """Get recent conversation history for context"""
        # For now, return empty list - can be enhanced with database storage
        return []
    
    def _update_conversation_history(self, user_message, bot_response):
        """Update conversation history"""
        # For now, just log - can be enhanced with database storage
        logger.info(f"User: {user_message}")
        logger.info(f"Bot: {bot_response}")
    
    def _get_fallback_response(self, user_message, os_type):
        """Provide fallback response when GPT-4o is unavailable"""
        # Analyze the user message for common IT issues
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['internet', 'wifi', 'network', 'connection']):
            return f"""**🌐 Network Connection Help**

I can help you troubleshoot your network connection on {os_type}! Here's what we can do:

**Quick Actions:**
• **Network Test** - Run connectivity diagnostics
• **Ping Test** - Check internet connectivity  
• **Network Config** - View network settings

**Common Network Commands:**
• `ping google.com` - Test basic connectivity
• `ipconfig` - View network configuration
• `nslookup google.com` - Test DNS resolution

Would you like me to run any of these diagnostics for you?"""
        
        elif any(word in message_lower for word in ['slow', 'freeze', 'crash', 'performance']):
            return f"""**⚡ Performance Issue Diagnosis**

I can help you diagnose performance issues on {os_type}! Let's identify the problem:

**Quick Actions:**
• **System Info** - View system details
• **Running Processes** - Check resource usage
• **Disk Space** - Verify storage availability

**Performance Commands:**
• `tasklist` - View running processes
• `systeminfo` - Get system specifications
• `wmic logicaldisk get size,freespace` - Check disk space

Let me know which diagnostic you'd like to run first!"""
        
        elif any(word in message_lower for word in ['install', 'program', 'software', 'application']):
            return f"""**📦 Software Installation Support**

I can help you with software installation issues on {os_type}! Here's how we can troubleshoot:

**Quick Actions:**
• **System Info** - Check system requirements
• **Running Processes** - See what's currently running
• **Directory Listing** - View file structure

**Installation Tips:**
• Check system requirements before installing
• Close unnecessary applications
• Run installer as administrator if needed
• Check available disk space

What software are you trying to install?"""
        
        elif any(word in message_lower for word in ['printer', 'scanner', 'hardware']):
            return f"""**🔌 Hardware Troubleshooting**

I can help you troubleshoot hardware issues on {os_type}! Let's diagnose the problem:

**Quick Actions:**
• **System Info** - View hardware details
• **Running Processes** - Check device drivers
• **Network Config** - For network devices

**Hardware Commands:**
• `wmic printer list brief` - List printers
• `devmgmt.msc` - Open device manager
• `systeminfo` - View hardware specs

What specific hardware issue are you experiencing?"""
        
        else:
            return f"""**🤖 IT Support Assistant**

I understand you're having an IT issue on {os_type}! I'm here to help you troubleshoot.

**Available Quick Actions:**
• **Network Test** - Check internet connectivity
• **System Info** - View system details  
• **Running Processes** - See active applications
• **Disk Space** - Check storage usage

**How I Can Help:**
1. **Diagnose** - Identify the root cause
2. **Guide** - Provide step-by-step solutions
3. **Execute** - Run system commands safely
4. **Monitor** - Track progress and results

Please describe your issue in detail, and I'll help you resolve it!"""
    
    def categorize_issue(self, user_message):
        """Categorize the IT issue based on keywords"""
        message_lower = user_message.lower()
        
        categories = {
            'network': ['internet', 'wifi', 'network', 'connection', 'ping', 'dns', 'ip'],
            'hardware': ['printer', 'scanner', 'keyboard', 'mouse', 'monitor', 'disk', 'memory'],
            'software': ['program', 'application', 'software', 'update', 'install', 'uninstall'],
            'system': ['slow', 'freeze', 'crash', 'error', 'blue screen', 'kernel'],
            'security': ['virus', 'malware', 'firewall', 'antivirus', 'password', 'login']
        }
        
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        
        return 'general' 

    def _add_diagnostic_suggestions(self, bot_response: str, user_message: str) -> str:
        """Add diagnostic suggestions to the bot response"""
        # Categorize the user's issue
        issue_category = self.automated_diagnostics.categorize_user_issue(user_message)
        
        # Get suggested diagnostics
        suggestions = self.automated_diagnostics.get_suggested_diagnostics(issue_category)
        
        if suggestions:
            # Format diagnostic suggestions
            diagnostic_text = self.automated_diagnostics.format_diagnostic_suggestions(suggestions)
            
            # Add to response if not already present
            if "🔍 Suggested Diagnostics:" not in bot_response:
                bot_response += "\n\n" + diagnostic_text
        
        return bot_response 