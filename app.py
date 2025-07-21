from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
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
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        os_type = os_detector.detect_os()
        response = chat_handler.process_message(user_message, os_type)
        
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        result = system_commands.execute_command(command)
        
        if result['success']:
            return jsonify({'success': True, 'output': result['output']})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Command failed')})
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

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

@app.route('/api/network-test')
def network_test():
    try:
        results = network_tools.run_basic_diagnostics()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in network test: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-test/macos')
def network_test_macos():
    """Get macOS-specific network information"""
    try:
        os_type = os_detector.detect_os()
        if os_type.lower() != 'darwin':
            return jsonify({'error': 'This endpoint is only for macOS'}), 400
        
        results = network_tools.get_macos_network_info()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in macOS network test: {str(e)}")
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
        
        if not command_text:
            return jsonify({'error': 'No command provided'}), 400
        
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
        if not user_message:
            return
        
        os_type = os_detector.detect_os()
        response = chat_handler.process_message(user_message, os_type)
        
        emit('bot_response', {
            'message': response,
            'timestamp': '2024-01-01T00:00:00Z'
        })
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 