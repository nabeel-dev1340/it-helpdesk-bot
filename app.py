from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import os
import sqlite3
from datetime import datetime
import uuid
from modules.chat_handler import ChatHandler
from modules.system_commands import SystemCommands
from modules.os_detector import OSDetector
from modules.network_tools import NetworkTools
from modules.security import SecurityValidator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            os_type TEXT
        )
    ''')
    
    # Command execution log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            command TEXT,
            output TEXT,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Initialize modules
chat_handler = ChatHandler()
system_commands = SystemCommands()
os_detector = OSDetector()
network_tools = NetworkTools()
security_validator = SecurityValidator()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages via REST API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get user's OS
        user_os = os_detector.detect_os()
        
        # Process message with GPT-4o
        bot_response = chat_handler.process_message(user_message, user_os)
        
        # Store in database
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (session_id, user_message, bot_response, os_type)
            VALUES (?, ?, ?, ?)
        ''', (session.get('session_id', 'unknown'), user_message, bot_response, user_os))
        conn.commit()
        conn.close()
        
        return jsonify({
            'response': bot_response,
            'os_type': user_os
        })
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    """Execute system command safely"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'Command cannot be empty'}), 400
        
        # Validate command security
        if not security_validator.is_command_safe(command):
            return jsonify({'error': 'Command not allowed for security reasons'}), 403
        
        # Execute command
        result = system_commands.execute_command(command)
        
        # Log command execution
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO command_logs (session_id, command, output, success)
            VALUES (?, ?, ?, ?)
        ''', (session.get('session_id', 'unknown'), command, result['output'], result['success']))
        conn.commit()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return jsonify({'error': 'Command execution failed'}), 500

@app.route('/api/system-info')
def system_info():
    """Get basic system information"""
    try:
        os_type = os_detector.detect_os()
        system_info = system_commands.get_system_info()
        
        return jsonify({
            'os_type': os_type,
            'system_info': system_info
        })
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': 'Failed to get system information'}), 500

@app.route('/api/network-test')
def network_test():
    """Perform basic network diagnostics"""
    try:
        results = network_tools.run_basic_diagnostics()
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error in network test: {str(e)}")
        return jsonify({'error': 'Network test failed'}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('send_message')
def handle_message(data):
    """Handle real-time chat messages"""
    try:
        user_message = data.get('message', '').strip()
        
        if not user_message:
            emit('error', {'message': 'Message cannot be empty'})
            return
        
        # Get user's OS
        user_os = os_detector.detect_os()
        
        # Process message with GPT-4o
        bot_response = chat_handler.process_message(user_message, user_os)
        
        # Store in database
        conn = sqlite3.connect('chat.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (session_id, user_message, bot_response, os_type)
            VALUES (?, ?, ?, ?)
        ''', (request.sid, user_message, bot_response, user_os))
        conn.commit()
        conn.close()
        
        # Emit response
        emit('bot_response', {
            'message': bot_response,
            'os_type': user_os,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {str(e)}")
        emit('error', {'message': 'Internal server error'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 