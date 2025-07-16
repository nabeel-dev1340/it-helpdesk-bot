# IT Help Bot 🤖

An intelligent IT support bot powered by GPT-4o that provides real-time troubleshooting assistance through a modern web chat interface. Built with Flask, WebSocket, and cross-platform system command execution.

## ✨ Features

### 🤖 AI-Powered Support
- **GPT-4o Integration**: Advanced natural language processing for understanding IT issues
- **Intelligent Responses**: Context-aware troubleshooting guidance
- **Multi-step Solutions**: Step-by-step problem resolution

### 🔒 Secure Command Execution
- **Command Whitelisting**: Only safe diagnostic commands allowed
- **OS-Specific Commands**: Windows, macOS, and Linux support
- **Security Validation**: Comprehensive input sanitization and validation
- **Audit Logging**: All command executions are logged

### 🌐 Network Diagnostics
- **Connectivity Tests**: Ping and traceroute functionality
- **DNS Resolution**: Domain lookup and troubleshooting
- **Network Configuration**: Interface and routing information
- **Real-time Results**: Live network status updates

### 💻 Cross-Platform Support
- **Windows**: Full cmd/PowerShell command support
- **macOS**: Terminal and system_profiler integration
- **Linux**: Unix command compatibility
- **OS Detection**: Automatic platform identification

### 🎨 Modern UI/UX
- **Real-time Chat**: WebSocket-powered instant messaging
- **Responsive Design**: Works on desktop and mobile
- **Typing Indicators**: Visual feedback during processing
- **Quick Actions**: One-click common diagnostics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd it-helpdesk-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Click "Start Chat" to begin troubleshooting

## 📁 Project Structure

```
it-helpdesk-bot/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── chat.db               # SQLite database (created automatically)
├── modules/              # Core application modules
│   ├── __init__.py
│   ├── chat_handler.py   # GPT-4o integration
│   ├── system_commands.py # Command execution
│   ├── os_detector.py    # OS detection
│   ├── network_tools.py  # Network diagnostics
│   └── security.py       # Security validation
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # Common JavaScript
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── chat.html         # Chat interface
└── tests/               # Test files
    └── test_basic.py     # Basic tests
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Security Settings
COMMAND_TIMEOUT=30
MAX_COMMAND_OUTPUT=10000
```

### API Endpoints

- `GET /` - Home page with system overview
- `GET /chat` - Chat interface
- `POST /api/chat` - Send message to bot
- `POST /api/execute-command` - Execute system command
- `GET /api/system-info` - Get system information
- `GET /api/network-test` - Run network diagnostics

## 🛡️ Security Features

### Command Whitelisting
Only approved diagnostic commands are allowed:

**Windows Commands:**
- `ipconfig`, `ping`, `nslookup`, `systeminfo`
- `tasklist`, `sfc`, `chkdsk`, `netstat`
- `tracert`, `route`, `arp`, `getmac`

**macOS Commands:**
- `ifconfig`, `ping`, `nslookup`, `system_profiler`
- `ps`, `diskutil`, `netstat`, `traceroute`
- `route`, `arp`, `networksetup`, `scutil`

**Linux Commands:**
- `ifconfig`, `ping`, `nslookup`, `ps`
- `netstat`, `df`, `free`, `uptime`

### Security Measures
- **Input Sanitization**: All user inputs are cleaned
- **Pattern Blocking**: Dangerous command patterns are blocked
- **Timeout Protection**: Commands have execution time limits
- **Audit Logging**: All actions are logged for security

## 🎯 Usage Examples

### Basic Troubleshooting
1. **Network Issues**: "My internet is not working"
2. **System Performance**: "My computer is running slow"
3. **Software Problems**: "I can't install this program"
4. **Hardware Issues**: "My printer won't connect"

### Quick Actions
- **Network Test**: One-click connectivity diagnostics
- **System Info**: Instant system overview
- **Process List**: View running applications
- **Disk Space**: Check storage usage

### Command Execution
The bot can suggest and execute safe system commands:
- `ping google.com` - Test internet connectivity
- `ipconfig` - View network configuration
- `systeminfo` - Get detailed system information
- `tasklist` - List running processes

## 🔍 Troubleshooting

### Common Issues

**OpenAI API Error**
- Verify your API key in `.env`
- Check your OpenAI account balance
- Ensure internet connectivity

**Command Execution Failed**
- Commands are restricted for security
- Check if command is in whitelist
- Verify OS compatibility

**WebSocket Connection Issues**
- Check if port 5000 is available
- Ensure firewall allows connections
- Try refreshing the page

### Debug Mode
Enable debug mode for detailed logging:
```env
FLASK_DEBUG=True
```

## 🧪 Testing

Run basic tests:
```bash
python -m pytest tests/
```

## 📊 Database Schema

### Chat History
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_message TEXT,
    bot_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    os_type TEXT
);
```

### Command Logs
```sql
CREATE TABLE command_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    command TEXT,
    output TEXT,
    success BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed for IT support and diagnostics. Users should:
- Only run commands they understand
- Be aware that system commands can affect their computer
- Use this tool responsibly and in accordance with their organization's policies

## 🆘 Support

For issues and questions:
- Check the troubleshooting section above
- Review the logs in the console
- Ensure all dependencies are installed
- Verify your OpenAI API key is valid

---

**Built with ❤️ using Flask, OpenAI GPT-4o, and modern web technologies**
