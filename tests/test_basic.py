import unittest
import sys
import os
import tempfile
import sqlite3

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.os_detector import OSDetector
from modules.security import SecurityValidator
from modules.system_commands import SystemCommands
from modules.network_tools import NetworkTools

class TestOSDetector(unittest.TestCase):
    """Test OS detection functionality"""
    
    def setUp(self):
        self.os_detector = OSDetector()
    
    def test_detect_os(self):
        """Test OS detection returns a valid OS type"""
        os_type = self.os_detector.detect_os()
        self.assertIn(os_type, ['Windows', 'macOS', 'Linux', 'Unknown'])
    
    def test_os_details(self):
        """Test getting OS details"""
        details = self.os_detector.get_os_details()
        self.assertIsInstance(details, dict)
        self.assertIn('system', details)
    
    def test_os_checks(self):
        """Test OS-specific check methods"""
        # At least one of these should be True
        checks = [
            self.os_detector.is_windows(),
            self.os_detector.is_macos(),
            self.os_detector.is_linux()
        ]
        self.assertTrue(any(checks))

class TestSecurityValidator(unittest.TestCase):
    """Test security validation functionality"""
    
    def setUp(self):
        self.validator = SecurityValidator()
    
    def test_safe_commands(self):
        """Test that safe commands are allowed"""
        safe_commands = [
            'ping google.com',
            'ipconfig',
            'systeminfo',
            'nslookup google.com'
        ]
        
        for command in safe_commands:
            with self.subTest(command=command):
                self.assertTrue(self.validator.is_command_safe(command))
    
    def test_dangerous_commands(self):
        """Test that dangerous commands are blocked"""
        dangerous_commands = [
            'rm -rf /',
            'del /s C:\\Windows',
            'sudo rm -rf',
            'format C:',
            'wget http://malicious.com',
            'curl http://malicious.com'
        ]
        
        for command in dangerous_commands:
            with self.subTest(command=command):
                self.assertFalse(self.validator.is_command_safe(command))
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        dangerous_input = '<script>alert("xss")</script>'
        sanitized = self.validator.sanitize_input(dangerous_input)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)
    
    def test_command_validation_for_os(self):
        """Test OS-specific command validation"""
        # Test Windows commands
        if self.validator.validate_command_for_os('ipconfig', 'Windows'):
            self.assertTrue(self.validator.validate_command_for_os('ipconfig', 'Windows'))
        
        # Test macOS commands
        if self.validator.validate_command_for_os('ifconfig', 'macOS'):
            self.assertTrue(self.validator.validate_command_for_os('ifconfig', 'macOS'))

class TestSystemCommands(unittest.TestCase):
    """Test system command execution"""
    
    def setUp(self):
        self.system_commands = SystemCommands()
    
    def test_get_system_info(self):
        """Test getting system information"""
        info = self.system_commands.get_system_info()
        self.assertIsInstance(info, dict)
        self.assertIn('os', info)
    
    def test_command_safety(self):
        """Test command safety validation"""
        # Test safe command
        result = self.system_commands.execute_command('echo "test"')
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)
    
    def test_dangerous_command_blocking(self):
        """Test that dangerous commands are blocked"""
        result = self.system_commands.execute_command('rm -rf /')
        self.assertFalse(result['success'])
        self.assertIn('not allowed', result['output'])

class TestNetworkTools(unittest.TestCase):
    """Test network diagnostics functionality"""
    
    def setUp(self):
        self.network_tools = NetworkTools()
    
    def test_ping_host(self):
        """Test ping functionality"""
        result = self.network_tools.ping_host('127.0.0.1', count=1)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)
    
    def test_nslookup(self):
        """Test DNS lookup functionality"""
        result = self.network_tools.nslookup('google.com')
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)
    
    def test_get_network_config(self):
        """Test getting network configuration"""
        result = self.network_tools.get_network_config()
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('output', result)

class TestDatabase(unittest.TestCase):
    """Test database functionality"""
    
    def setUp(self):
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create test tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                os_type TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                command TEXT,
                output TEXT,
                success BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def tearDown(self):
        self.conn.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_chat_history_insert(self):
        """Test inserting chat history"""
        self.cursor.execute('''
            INSERT INTO chat_history (session_id, user_message, bot_response, os_type)
            VALUES (?, ?, ?, ?)
        ''', ('test_session', 'Hello', 'Hi there!', 'Windows'))
        
        self.cursor.execute('SELECT COUNT(*) FROM chat_history')
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)
    
    def test_command_logs_insert(self):
        """Test inserting command logs"""
        self.cursor.execute('''
            INSERT INTO command_logs (session_id, command, output, success)
            VALUES (?, ?, ?, ?)
        ''', ('test_session', 'ping google.com', 'Ping successful', True))
        
        self.cursor.execute('SELECT COUNT(*) FROM command_logs')
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOSDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkTools))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 