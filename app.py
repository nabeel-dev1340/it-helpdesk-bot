from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
from config import Config
from modules.chat_handler import ChatHandler
from modules.network_tools import NetworkTools
from modules.system_commands import SystemCommands
from modules.os_detector import OSDetector
from modules.automated_diagnostics import AutomatedDiagnostics, DiagnosticCommand
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize modules
chat_handler = ChatHandler()
network_tools = NetworkTools()
system_commands = SystemCommands()
os_detector = OSDetector()
automated_diagnostics = AutomatedDiagnostics()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_old_sessions():
    """Clean up old sessions periodically"""
    try:
        chat_handler.chat_database.cleanup_old_sessions(days=30)
        logger.info("Cleaned up old sessions")
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")

# Schedule cleanup every 24 hours
import threading
import time

def schedule_cleanup():
    """Schedule periodic cleanup of old sessions"""
    while True:
        time.sleep(24 * 60 * 60)  # 24 hours
        cleanup_old_sessions()

# Start cleanup thread
cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/system-info')
def get_system_info():
    try:
        os_type = os_detector.detect_os()
        system_info = system_commands.get_system_info()
        return jsonify({
            'os_type': os_type,
            'system_info': system_info
        })
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', None)
        os_type = data.get('os_type', os_detector.detect_os())
        
        result = chat_handler.process_message(user_message, os_type, session_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_system_command():
    try:
        data = request.get_json()
        command = data.get('command', '')
        password = data.get('password', None)
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Set sudo password if provided for macOS
        if password and os_detector.is_macos():
            system_commands.set_sudo_password(password)
        
        # Check if command requires sudo on macOS
        require_sudo = system_commands._requires_sudo(command) if os_detector.is_macos() else False
        
        result = system_commands.execute_command(command, require_sudo=require_sudo)
        
        if result.get('requires_password'):
            return jsonify({
                'success': False,
                'error': 'Sudo password required for this command',
                'requires_password': True
            })
        
        if result['success']:
            return jsonify({'success': True, 'output': result['output']})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Command failed')})
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/set-password', methods=['POST'])
def set_sudo_password():
    """Set sudo password for macOS commands"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        if not os_detector.is_macos():
            return jsonify({'error': 'Password setting is only available on macOS'}), 400
        
        system_commands.set_sudo_password(password)
        return jsonify({'success': True, 'message': 'Password set successfully'})
    except Exception as e:
        logger.error(f"Error setting password: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the command cache"""
    try:
        system_commands.clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/stats')
def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = system_commands.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        data = request.get_json()
        os_type = data.get('os_type', os_detector.detect_os())
        
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Create session in database
        chat_handler.chat_database.create_session(session_id, os_type)
        
        return jsonify({
            'session_id': session_id,
            'os_type': os_type,
            'message': 'Session created successfully'
        })
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/history')
def get_session_history(session_id):
    """Get conversation history for a session"""
    try:
        history = chat_handler.chat_database.get_conversation_history(session_id, limit=20)
        session_info = chat_handler.chat_database.get_session_info(session_id)
        
        return jsonify({
            'session_info': session_info,
            'history': history
        })
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/stats')
def get_session_stats():
    """Get session statistics"""
    try:
        stats = chat_handler.chat_database.get_session_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting session stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-test')
def network_test():
    try:
        results = network_tools.run_basic_diagnostics()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in network test: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network/status')
def check_network_status():
    """Check internet connectivity status"""
    try:
        internet_available = network_tools.check_internet_connectivity()
        dns_working = network_tools.check_dns_resolution()
        
        return jsonify({
            'internet_available': internet_available,
            'dns_working': dns_working,
            'status': 'connected' if internet_available else 'disconnected'
        })
    except Exception as e:
        logger.error(f"Error checking network status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network/fallback-commands')
def get_network_fallback_commands():
    """Get fallback commands for network issues"""
    try:
        os_type = os_detector.detect_os()
        fallback_data = network_tools.get_network_fallback_commands(os_type)
        
        return jsonify({
            'os_type': os_type,
            'commands': fallback_data['diagnostic_commands'],
            'troubleshooting_steps': fallback_data['troubleshooting_steps']
        })
    except Exception as e:
        logger.error(f"Error getting fallback commands: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnostics/suggest', methods=['POST'])
def suggest_diagnostics():
    """Get suggested diagnostics based on user message"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Categorize the issue
        issue_category = automated_diagnostics.categorize_user_issue(user_message)
        
        # Get suggested diagnostics
        suggestions = automated_diagnostics.get_suggested_diagnostics(issue_category)
        
        # Convert to serializable format
        diagnostic_list = []
        for cmd in suggestions:
            diagnostic_list.append({
                'name': cmd.name,
                'description': cmd.description,
                'command': cmd.command,
                'category': cmd.category,
                'risk_level': cmd.risk_level
            })
        
        return jsonify({
            'issue_category': issue_category,
            'suggestions': diagnostic_list
        })
    except Exception as e:
        logger.error(f"Error suggesting diagnostics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnostics/execute', methods=['POST'])
def execute_diagnostic():
    """Execute a diagnostic command with user permission"""
    try:
        data = request.get_json()
        command_name = data.get('command_name', '')
        command_text = data.get('command', '')
        password = data.get('password', None)
        
        if not command_text:
            return jsonify({'error': 'No command provided'}), 400
        
        # Set sudo password if provided for macOS
        if password and os_detector.is_macos():
            system_commands.set_sudo_password(password)
        
        # Check if command requires sudo on macOS
        require_sudo = system_commands._requires_sudo(command_text) if os_detector.is_macos() else False
        
        # Create a diagnostic command object
        diagnostic_cmd = DiagnosticCommand(
            name=command_name or "Custom Command",
            description="User-approved diagnostic command",
            command=command_text,
            category="custom",
            risk_level="low"
        )
        
        # Execute the command
        success, output = automated_diagnostics.execute_command(diagnostic_cmd)
        
        if success:
            return jsonify({
                'success': True,
                'output': output,
                'command_name': command_name
            })
        else:
            return jsonify({
                'success': False,
                'error': output,
                'command_name': command_name
            })
    except Exception as e:
        logger.error(f"Error executing diagnostic: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnostics/available')
def get_available_diagnostics():
    """Get all available diagnostic commands"""
    try:
        all_commands = {}
        for category, commands in automated_diagnostics.diagnostic_commands.items():
            all_commands[category] = []
            for cmd in commands:
                all_commands[category].append({
                    'name': cmd.name,
                    'description': cmd.description,
                    'command': cmd.command,
                    'category': cmd.category,
                    'risk_level': cmd.risk_level
                })
        
        return jsonify(all_commands)
    except Exception as e:
        logger.error(f"Error getting available diagnostics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/command/execute', methods=['POST'])
def execute_gpt_command():
    """Execute a command suggested by GPT-4o"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        description = data.get('description', '')
        session_id = data.get('session_id')
        password = data.get('password', None)
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Set sudo password if provided for macOS
        if password and os_detector.is_macos():
            system_commands.set_sudo_password(password)
        
        # Check if command requires sudo on macOS
        require_sudo = system_commands._requires_sudo(command) if os_detector.is_macos() else False
        
        # Execute the command
        result = system_commands.execute_command(command, require_sudo=require_sudo)
        
        # Store command execution in database
        if session_id:
            chat_handler.chat_database.store_command_execution(
                session_id, command, description, 
                result.get('output', ''), result.get('error', ''),
                result.get('success', False)
            )
        
        return jsonify({
            'success': result.get('success', False),
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'command': command,
            'description': description,
            'requires_password': result.get('requires_password', False)
        })
        
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({'error': f'Error executing command: {str(e)}'}), 500

@app.route('/api/command/analyze', methods=['POST'])
def analyze_command_result():
    data = request.get_json()
    session_id = data.get('session_id')
    command = data.get('command')
    output = data.get('output')
    error = data.get('error')
    success = data.get('success', True)
    user_message = data.get('user_message', '')
    previous_bot_response = data.get('previous_bot_response', '')

    # Compose context for GPT-4o
    context = [
        {"role": "user", "content": user_message or "The user asked for help."},
        {"role": "assistant", "content": previous_bot_response or "The assistant provided a diagnosis and suggested a command."},
        {"role": "user", "content": f"I ran the command `{command}`. Here is the result:\nOutput:\n{output or '(no output)'}\nError:\n{error or 'None'}"}
    ]
    prompt = (
        "Given the user's issue, your previous diagnosis, and the command result, "
        "analyze the result and provide actionable insights or next steps. "
        "If the issue is resolved, say so. If not, suggest what to try next."
    )
    context.insert(0, {"role": "system", "content": prompt})

    # Call GPT-4o
    try:
        import openai
        client=openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=context,
            max_tokens=Config.OPENAI_MAX_TOKENS,
            temperature=Config.OPENAI_TEMPERATURE
        )
        bot_followup = response.choices[0].message.content
        # Optionally store this in the session history
        chat_handler.chat_database.store_message(
            session_id, f"Command result for {command}", bot_followup, "system", "gpt_analysis"
        )
        return jsonify({"response": bot_followup})
    except Exception as e:
        import logging
        logging.exception("Error in /api/command/analyze")
        return jsonify({"response": "Sorry, I could not analyze the command result."}), 500

@app.route('/api/commands/get', methods=['GET'])
def get_session_commands():
    """Get commands for the current session"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
        
        # Get commands from database (you can implement this based on your storage)
        # For now, return empty array
        commands = []
        
        return jsonify({
            'commands': commands,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error getting session commands: {str(e)}")
        return jsonify({'error': f'Error getting commands: {str(e)}'}), 500

@app.route('/api/test-json', methods=['POST'])
def test_json_parsing():
    """Test endpoint to verify JSON parsing"""
    try:
        data = request.get_json()
        test_response = data.get('test_response', '')
        
        # Simulate the JSON parsing logic
        import json
        try:
            parsed = json.loads(test_response)
            response_text = parsed.get('response', '')
            system_commands = parsed.get('system_commands', [])
            escalation = parsed.get('escalation', False)
            
            return jsonify({
                'success': True,
                'parsed': {
                    'response_text': response_text,
                    'system_commands': system_commands,
                    'escalation': escalation
                }
            })
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'raw_response': test_response
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    # Don't send automatic welcome message - let the user initiate the conversation

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    try:
        user_message = data.get('message', '')
        session_id = data.get('session_id', None)
        
        if not user_message:
            return
        
        os_type = os_detector.detect_os()
        response = chat_handler.process_message(user_message, os_type, session_id)
        
        emit('bot_response', {
            'message': response,
            'timestamp': '2024-01-01T00:00:00Z'
        })
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 