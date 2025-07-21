import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class ChatDatabase:
    """Handles conversation history storage and retrieval"""
    
    def __init__(self, db_path: str = None):
        """Initialize the chat database"""
        self.db_path = db_path or Config.DATABASE_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        bot_response TEXT NOT NULL,
                        os_type TEXT,
                        intent_category TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        message_type TEXT DEFAULT 'chat'
                    )
                ''')
                
                # Create sessions table for tracking conversation sessions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        os_type TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0
                    )
                ''')
                
                # Create command_executions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS command_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        command TEXT,
                        description TEXT,
                        output TEXT,
                        error TEXT,
                        success BOOLEAN,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_id 
                    ON conversation_history(session_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON conversation_history(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_activity 
                    ON chat_sessions(last_activity)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def store_message(self, session_id: str, user_message: str, bot_response: str, 
                     os_type: str = None, intent_category: str = None, message_type: str = 'chat'):
        """Store a message exchange in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert the message exchange
                cursor.execute('''
                    INSERT INTO conversation_history 
                    (session_id, user_message, bot_response, os_type, intent_category, message_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, user_message, bot_response, os_type, intent_category, message_type))
                
                # Update session activity
                cursor.execute('''
                    INSERT OR REPLACE INTO chat_sessions 
                    (session_id, os_type, last_activity, message_count)
                    VALUES (?, ?, CURRENT_TIMESTAMP, 
                        COALESCE((SELECT message_count FROM chat_sessions WHERE session_id = ?), 0) + 1)
                ''', (session_id, os_type, session_id))
                
                conn.commit()
                logger.debug(f"Stored message for session {session_id}")
                
        except Exception as e:
            logger.error(f"Error storing message: {str(e)}")
    
    def get_conversation_history(self, session_id: str, limit: int = 15) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_message, bot_response, timestamp, intent_category
                    FROM conversation_history 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (session_id, limit))
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries and reverse to get chronological order
                history = []
                for row in reversed(rows):
                    history.append({
                        'user_message': row[0],
                        'bot_response': row[1],
                        'timestamp': row[2],
                        'intent_category': row[3]
                    })
                
                logger.debug(f"Retrieved {len(history)} messages for session {session_id}")
                return history
                
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a specific session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, os_type, created_at, last_activity, message_count
                    FROM chat_sessions 
                    WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'session_id': row[0],
                        'os_type': row[1],
                        'created_at': row[2],
                        'last_activity': row[3],
                        'message_count': row[4]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving session info: {str(e)}")
            return None
    
    def create_session(self, session_id: str, os_type: str = None) -> bool:
        """Create a new chat session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO chat_sessions 
                    (session_id, os_type, created_at, last_activity, message_count)
                    VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                ''', (session_id, os_type))
                
                conn.commit()
                logger.info(f"Created new session: {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return False
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old sessions and messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Delete old conversation history
                cursor.execute('''
                    DELETE FROM conversation_history 
                    WHERE timestamp < ?
                ''', (cutoff_date,))
                
                # Delete old sessions
                cursor.execute('''
                    DELETE FROM chat_sessions 
                    WHERE last_activity < ?
                ''', (cutoff_date,))
                
                conn.commit()
                logger.info(f"Cleaned up sessions older than {days} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {str(e)}")
    
    def get_session_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total messages
                cursor.execute('SELECT COUNT(*) FROM conversation_history')
                total_messages = cursor.fetchone()[0]
                
                # Get total sessions
                cursor.execute('SELECT COUNT(*) FROM chat_sessions')
                total_sessions = cursor.fetchone()[0]
                
                # Get active sessions (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM chat_sessions 
                    WHERE last_activity > datetime('now', '-1 day')
                ''')
                active_sessions = cursor.fetchone()[0]
                
                return {
                    'total_messages': total_messages,
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions
                }
                
        except Exception as e:
            logger.error(f"Error getting session stats: {str(e)}")
            return {} 

    def store_command_execution(self, session_id, command, description, output, error, success):
        """Store command execution results in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO command_executions 
                    (session_id, command, description, output, error, success, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, command, description, output, error, success, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing command execution: {str(e)}")
    
    def get_command_executions(self, session_id, limit=10):
        """Get command executions for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT command, description, output, error, success, timestamp
                    FROM command_executions 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting command executions: {str(e)}")
            return [] 