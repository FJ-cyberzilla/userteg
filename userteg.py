
#!/usr/bin/env python3
"""
USERTEG - Advanced Telegram OSINT Command Center
Professional Intelligence Gathering System
"""

import os
import sys
import json
import time
import sqlite3
import requests
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# ============================================================================
# COLOR SYSTEM - Vintage Blue Gradient Theme
# ============================================================================

class Colors:
    # Gradient Blues
    BLUE1 = '\033[38;5;25m'   # Deep Blue
    BLUE2 = '\033[38;5;26m'   # Royal Blue
    BLUE3 = '\033[38;5;27m'   # Bright Blue
    CYAN1 = '\033[38;5;31m'   # Deep Cyan
    CYAN2 = '\033[38;5;37m'   # Bright Cyan
    CYAN3 = '\033[38;5;45m'   # Light Cyan

    # Status Colors
    SUCCESS = '\033[38;5;46m'  # Green
    WARNING = '\033[38;5;226m' # Yellow
    ERROR = '\033[38;5;196m'   # Red
    INFO = '\033[38;5;117m'    # Light Blue

    # Special
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    BLINK = '\033[5m'

# ============================================================================
# FOLDER STRUCTURE MANAGER
# ============================================================================

class FolderStructure:
    """Manages organized folder structure for USERTEG"""

    def __init__(self, base_dir: str = "userteg_data"):
        self.base_dir = Path(base_dir)
        self.folders = {
            'database': self.base_dir / 'database',
            'logs': self.base_dir / 'logs',
            'exports': self.base_dir / 'exports',
            'downloads': self.base_dir / 'downloads',
            'profiles': self.base_dir / 'downloads' / 'profiles',
            'media': self.base_dir / 'downloads' / 'media',
            'config': self.base_dir / 'config',
            'cache': self.base_dir / 'cache'
        }

    def initialize(self):
        """Create all necessary folders"""
        for folder_path in self.folders.values():
            folder_path.mkdir(parents=True, exist_ok=True)

        # Create README
        readme_path = self.base_dir / 'README.txt'
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(self._get_readme_content())

        print(f"{Colors.SUCCESS}✓ Folder structure initialized{Colors.RESET}")

    def _get_readme_content(self):
        return """
╔═══════════════════════════════════════════════════════════╗
║           USERTEG DATA DIRECTORY STRUCTURE                ║
╚═══════════════════════════════════════════════════════════╝

📁 database/     - SQLite intelligence database
📁 logs/         - Operation logs and activity records
📁 exports/      - JSON exports and reports
📁 downloads/
   └─ profiles/  - User profile photos
   └─ media/     - Downloaded media files
📁 config/       - Configuration files
📁 cache/        - Temporary cache data

⚠️  SECURITY: Keep this directory secure and private
⚠️  BACKUP: Regularly backup the database folder
"""

    def get_path(self, key: str) -> Path:
        """Get path for specific folder"""
        return self.folders.get(key, self.base_dir)

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Manages bot configuration and API tokens"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / 'config.json'
        self.token_file = config_dir / '.token'

    def load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def save_token(self, token: str):
        """Securely save bot token"""
        with open(self.token_file, 'w') as f:
            f.write(token)
        # Set restrictive permissions (Unix-like systems)
        try:
            os.chmod(self.token_file, 0o600)
        except:
            pass
        print(f"{Colors.SUCCESS}✓ Token saved securely{Colors.RESET}")

    def load_token(self) -> Optional[str]:
        """Load saved bot token"""
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                return f.read().strip()
        return None

    def token_exists(self) -> bool:
        """Check if token is saved"""
        return self.token_file.exists()

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manages all SQLite database interactions for USERTEG"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                current_username TEXT,
                is_bot INTEGER,
                language_code TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP
            )
        ''')

        # Username history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS username_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                changed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER,
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                message_text TEXT,
                message_date TIMESTAMP,
                media_type TEXT,
                forwarded_from INTEGER,
                reply_to_message_id INTEGER,
                PRIMARY KEY (message_id, chat_id)
            )
        ''')

        # Chats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT,
                title TEXT,
                username TEXT,
                description TEXT,
                member_count INTEGER,
                first_seen TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')

        # User activity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                chat_title TEXT,
                status TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def store_message_data(self, message_id: int, chat_id: int, user_id: int,
                           username: Optional[str], first_name: Optional[str],
                           message_text: str, message_date: str, media_type: Optional[str],
                           forwarded_from: Optional[int], reply_to_message_id: Optional[int]):
        """Store message data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO messages
            (message_id, chat_id, user_id, username, first_name, message_text, message_date, media_type, forwarded_from, reply_to_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, chat_id, user_id, username, first_name, message_text,
              message_date, media_type, forwarded_from, reply_to_message_id))

        conn.commit()
        conn.close()

    def search_usernames(self, username_query: str) -> List[Dict]:
        """Search for usernames (current and historical) in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT u.user_id, u.first_name, u.current_username
            FROM users u
            LEFT JOIN username_history uh ON u.user_id = uh.user_id
            WHERE u.current_username LIKE ? OR uh.username LIKE ?
        ''', (f'%{username_query}%', f'%{username_query}%'))

        results = []
        for uid, first_name, current_username in cursor.fetchall():
            results.append({
                'user_id': uid,
                'first_name': first_name,
                'current_username': current_username
            })
        conn.close()
        return results

    def get_user_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's message history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT m.*, c.title as chat_title
            FROM messages m
            LEFT JOIN chats c ON m.chat_id = c.chat_id
            WHERE m.user_id = ?
            ORDER BY m.message_date DESC
            LIMIT ?
        ''', (user_id, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'message_id': row[0],
                'chat_id': row[1],
                'username': row[3],
                'first_name': row[4],
                'text': row[5],
                'date': row[6],
                'media_type': row[7],
                'chat_title': row[10] if len(row) > 10 else 'Unknown'
            })

        conn.close()
        return messages

    def get_username_history(self, user_id: int) -> List[Dict]:
        """Get username change history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, changed_at
            FROM username_history
            WHERE user_id = ?
            ORDER BY changed_at DESC
        ''', (user_id,))

        history = [{'username': row[0], 'changed_at': row[1]} for row in cursor.fetchall()]
        conn.close()
        return history

# ============================================================================
# BANNER SYSTEM
# ============================================================================

class BannerDisplay:
    """Vintage blue gradient ASCII banner system"""

    @staticmethod
    def show_main_banner():
        banner = f"""
{Colors.BLUE1}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
{Colors.BLUE2}    ║   ██╗   ██╗███████╗███████╗██████╗ ████████╗███████╗ ██████╗   ║
    ║   ██║   ██║██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔════╝   ║
{Colors.BLUE3}    ║   ██║   ██║███████╗█████╗  ██████╔╝   ██║   █████╗  ██║  ███╗  ║
    ║   ██║   ██║╚════██║██╔══╝  ██╔══██╗   ██║   ██╔══╝  ██║   ██║  ║
{Colors.CYAN1}    ║   ╚██████╔╝███████║███████╗██║  ██║   ██║   ███████╗╚██████╔╝  ║
    ║    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝     ║
{Colors.CYAN2}    ║                                                    ║
    ║            TELEGRAM OSINT COMMAND CENTER v2.0                    ║
{Colors.CYAN3}    ║  Cyberzilla™ - Autumn MMXXV                   ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.INFO}    [•] Real-time Message Monitoring    [•] Username History Tracking
    [•] Deep User Intelligence          [•] Chat Analytics & Statistics
    [•] Multi-Group Surveillance        [•] Automated Data Collection{Colors.RESET}
"""
        print(banner)

    @staticmethod
    def show_section_header(title: str):
        width = 70
        print(f"\n{Colors.BLUE2}{Colors.BOLD}{'═' * width}")
        print(f"  {title.upper()}")
        print(f"{'═' * width}{Colors.RESET}\n")

    @staticmethod
    def show_loading(message: str):
        print(f"{Colors.CYAN2}[{Colors.BLINK}●{Colors.RESET}{Colors.CYAN2}] {message}...{Colors.RESET}", end='', flush=True)

    @staticmethod
    def show_success(message: str):
        print(f"\r{Colors.SUCCESS}[✓] {message}{Colors.RESET}")

    @staticmethod
    def show_error(message: str):
        print(f"\r{Colors.ERROR}[✗] {message}{Colors.RESET}")

    @staticmethod
    def show_warning(message: str):
        print(f"{Colors.WARNING}[!] {message}{Colors.RESET}")

    @staticmethod
    def show_info(message: str):
        print(f"{Colors.INFO}[i] {message}{Colors.RESET}")

# ============================================================================
# MAIN OSINT ENGINE
# ============================================================================

class UserTegOSINT:
    def __init__(self, token: str, folders: FolderStructure):
        self.token = token
        self.folders = folders
        self.session = requests.Session()
        self.base_url = f"https://api.telegram.org/bot{token}"

        # Setup paths
        self.db_manager = DatabaseManager(folders.get_path('database') / 'intelligence.db')
        self.log_file = folders.get_path('logs') / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def log_operation(self, operation: str, data: Any):
        """Log operations to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'data': data
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def api_call(self, method: str, params: Dict = None) -> Dict:
        """Generic API call handler"""
        try:
            url = f"{self.base_url}/{method}"
            response = self.session.get(url, params=params, timeout=15)
            data = response.json()

            if data.get('ok'):
                return {'success': True, 'data': data['result']}
            else:
                return {'success': False, 'error': data.get('description', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def validate_token(self) -> bool:
        """Validate bot token"""
        result = self.api_call('getMe')
        return result.get('success', False)

    def process_message(self, message: Dict):
        """Process and store incoming message"""
        chat = message.get('chat', {})
        chat_id = chat.get('id')
        user = message.get('from', {})
        user_id = user.get('id')

        if not all([message.get('message_id'), chat_id, user_id]):
            return

        self.db_manager.store_user_data(user)

        message_text = message.get('text', '')
        message_date = datetime.fromtimestamp(message.get('date', 0)).isoformat()

        media_type = None
        if 'photo' in message:
            media_type = 'photo'
        elif 'video' in message:
            media_type = 'video'
        elif 'document' in message:
            media_type = 'document'

        # Now using db_manager for message storage
        self.db_manager.store_message_data(
            message_id=message.get('message_id'),
            chat_id=chat_id,
            user_id=user_id,
            username=user.get('username'),
            first_name=user.get('first_name'),
            message_text=message_text,
            message_date=message_date,
            media_type=media_type,
            forwarded_from=message.get('forward_from', {}).get('id'),
            reply_to_message_id=message.get('reply_to_message', {}).get('message_id')
        )

        print(f"{Colors.SUCCESS}[+] Logged: @{user.get('username', user_id)} in {chat.get('title', chat_id)}{Colors.RESET}")

class DatabaseManager:
    """Manages all SQLite database interactions for USERTEG"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                current_username TEXT,
                is_bot INTEGER,
                language_code TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP
            )
        ''')

        # Username history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS username_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                changed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER,
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                message_text TEXT,
                message_date TIMESTAMP,
                media_type TEXT,
                forwarded_from INTEGER,
                reply_to_message_id INTEGER,
                PRIMARY KEY (message_id, chat_id)
            )
        ''')

        # Chats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT,
                title TEXT,
                username TEXT,
                description TEXT,
                member_count INTEGER,
                first_seen TIMESTAMP,
                last_updated TIMESTAMP
            )
        ''')

        # User activity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                chat_title TEXT,
                status TEXT,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def store_message_data(self, message_id: int, chat_id: int, user_id: int,
                           username: Optional[str], first_name: Optional[str],
                           message_text: str, message_date: str, media_type: Optional[str],
                           forwarded_from: Optional[int], reply_to_message_id: Optional[int]):
        """Store message data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO messages
            (message_id, chat_id, user_id, username, first_name, message_text, message_date, media_type, forwarded_from, reply_to_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, chat_id, user_id, username, first_name, message_text,
              message_date, media_type, forwarded_from, reply_to_message_id))

        conn.commit()
        conn.close()

    def search_usernames(self, username_query: str) -> List[Dict]:
        """Search for usernames (current and historical) in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT u.user_id, u.first_name, u.current_username
            FROM users u
            LEFT JOIN username_history uh ON u.user_id = uh.user_id
            WHERE u.current_username LIKE ? OR uh.username LIKE ?
        ''', (f'%{username_query}%', f'%{username_query}%'))

        results = []
        for uid, first_name, current_username in cursor.fetchall():
            results.append({
                'user_id': uid,
                'first_name': first_name,
                'current_username': current_username
            })
        conn.close()
        return results

    def get_user_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's message history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT m.*, c.title as chat_title
            FROM messages m
            LEFT JOIN chats c ON m.chat_id = c.chat_id
            WHERE m.user_id = ?
            ORDER BY m.message_date DESC
            LIMIT ?
        ''', (user_id, limit))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'message_id': row[0],
                'chat_id': row[1],
                'username': row[3],
                'first_name': row[4],
                'text': row[5],
                'date': row[6],
                'media_type': row[7],
                'chat_title': row[10] if len(row) > 10 else 'Unknown'
            })

        conn.close()
        return messages

    def get_username_history(self, user_id: int) -> List[Dict]:
        """Get username change history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, changed_at
            FROM username_history
            WHERE user_id = ?
            ORDER BY changed_at DESC
        ''', (user_id,))

        history = [{'username': row[0], 'changed_at': row[1]} for row in cursor.fetchall()]
        conn.close()
        return history

# ============================================================================
# BANNER SYSTEM

    def get_username_history(self, user_id: int) -> List[Dict]:
        """Get username change history"""
        return self.db_manager.get_username_history(user_id)

    def search_messages(self, keyword: str, limit: int = 100) -> List[Dict]:
        """Search messages by keyword"""
        return self.db_manager.search_messages(keyword, limit)

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        return self.db_manager.get_database_stats()

    def start_monitoring(self):
        """Start message monitoring"""
        BannerDisplay.show_section_header("MESSAGE MONITORING ACTIVE")
        BannerDisplay.show_info("Bot is now logging all messages from groups it's in")
        BannerDisplay.show_warning("Press Ctrl+C to stop monitoring")
        print()

        last_update_id = 0

        try:
            while True:
                response = self.session.get(
                    f"{self.base_url}/getUpdates",
                    params={'offset': last_update_id + 1, 'timeout': 30}
                )

                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])

                    for update in updates:
                        last_update_id = update['update_id']

                        if 'message' in update:
                            self.process_message(update['message'])

                time.sleep(0.1)

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] Monitoring stopped{Colors.RESET}")

# ============================================================================
# INTERACTIVE MENU SYSTEM
# ============================================================================

class MenuSystem:
    def __init__(self, osint: UserTegOSINT):
        self.osint = osint

    def show_menu(self):
        print(f"\n{Colors.BLUE2}{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗")
        print(f"║              USERTEG COMMAND CENTER - MAIN MENU                ║")
        print(f"╚════════════════════════════════════════════════════════════════╝{Colors.RESET}")

        options = [
            ("Intelligence Gathering", [
                "View User Intelligence & History",
                "Search Username (Current + Historical)",
                "View User's Message History",
                "Search Messages by Keyword"
            ]),
            ("Real-time Monitoring", [
                "START Message Monitoring (24/7)",
                "View Live Database Statistics"
            ]),
            ("Analysis & Reports", [
                "Generate Intelligence Report",
                "Export Data to JSON"
            ]),
            ("System", [
                "View Session Logs",
                "Bot Information",
                "Exit USERTEG"
            ])
        ]

        counter = 1
        for category, items in options:
            print(f"\n{Colors.CYAN2}{Colors.BOLD}  {category}:{Colors.RESET}")
            for item in items:
                print(f"{Colors.CYAN3}    [{counter:2d}] {item}{Colors.RESET}")
                counter += 1

    def handle_choice(self, choice: int):
        if choice == 1:
            self.view_user_intelligence()
        elif choice == 2:
            self.search_username()
        elif choice == 3:
            self.view_message_history()
        elif choice == 4:
            self.search_messages()
        elif choice == 5:
            self.osint.start_monitoring()
        elif choice == 6:
            self.show_statistics()
        elif choice == 7:
            self.generate_report()
        elif choice == 8:
            self.export_data()
        elif choice == 9:
            self.view_logs()
        elif choice == 10:
            self.show_bot_info()
        elif choice == 11:
            return False
        return True

    def view_user_intelligence(self):
        BannerDisplay.show_section_header("User Intelligence Lookup")
        user_id = input(f"{Colors.CYAN2}[?] Enter User ID: {Colors.RESET}").strip()

        if not user_id.isdigit():
            BannerDisplay.show_error("Invalid User ID")
            return

        history = self.osint.get_username_history(int(user_id))
        messages = self.osint.get_user_messages(int(user_id), 10)

        print(f"\n{Colors.INFO}{'─' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}User ID: {user_id}{Colors.RESET}")

        if history:
            print(f"\n{Colors.WARNING}Username History:{Colors.RESET}")
            for idx, h in enumerate(history, 1):
                print(f"  {idx}. @{h['username']} - {h['changed_at']}")

        if messages:
            print(f"\n{Colors.SUCCESS}Recent Messages ({len(messages)}):{Colors.RESET}")
            for idx, msg in enumerate(messages[:5], 1):
                print(f"\n  [{idx}] {msg['date']}")
                print(f"      Chat: {msg['chat_title']}")
                print(f"      {msg['text'][:100]}...")

    def search_username(self):
        BannerDisplay.show_section_header("Username Search")
        username = input(f"{Colors.CYAN2}[?] Enter username: {Colors.RESET}").strip()

        results = self.osint.db_manager.search_usernames(username)

        if results:
            print(f"\n{Colors.SUCCESS}Found {len(results)} match(es):{Colors.RESET}")
            for idx, res in enumerate(results, 1):
                print(f"  {idx}. {res['first_name']} (@{res['current_username']}) - ID: {res['user_id']}")
        else:
            BannerDisplay.show_warning("No matches found")

    def view_message_history(self):
        BannerDisplay.show_section_header("Message History Viewer")
        user_id = input(f"{Colors.CYAN2}[?] Enter User ID: {Colors.RESET}").strip()

        if not user_id.isdigit():
            BannerDisplay.show_error("Invalid User ID")
            return

        messages = self.osint.get_user_messages(int(user_id), 50)

        if messages:
            print(f"\n{Colors.SUCCESS}Found {len(messages)} messages:{Colors.RESET}\n")
            for idx, msg in enumerate(messages, 1):
                print(f"{Colors.CYAN3}[{idx}] {msg['date']}{Colors.RESET}")
                print(f"    {Colors.DIM}Chat:{Colors.RESET} {msg['chat_title']}")
                print(f"    {Colors.DIM}From:{Colors.RESET} {msg['first_name']} (@{msg['username']})")
                print(f"    {msg['text'][:150]}")
                print()
        else:
            BannerDisplay.show_warning("No messages found")

    def search_messages(self):
        BannerDisplay.show_section_header("Message Keyword Search")
        keyword = input(f"{Colors.CYAN2}[?] Enter keyword: {Colors.RESET}").strip()

        messages = self.osint.search_messages(keyword, 50)

        if messages:
            print(f"\n{Colors.SUCCESS}Found {len(messages)} messages:{Colors.RESET}\n")
            for idx, msg in enumerate(messages, 1):
                print(f"{Colors.CYAN3}[{idx}]{Colors.RESET} @{msg['username']}: {msg['text'][:100]}...")
        else:
            BannerDisplay.show_warning("No messages found")

    def show_statistics(self):
        BannerDisplay.show_section_header("Database Statistics")
        stats = self.osint.get_database_stats()

        print(f"{Colors.INFO}Total Users Tracked:{Colors.RESET}      {stats['users']}")
        print(f"{Colors.INFO}Total Messages Logged:{Colors.RESET}    {stats['messages']}")
        print(f"{Colors.INFO}Total Chats Monitored:{Colors.RESET}    {stats['chats']}")
        print(f"{Colors.INFO}Username Changes:{Colors.RESET}         {stats['username_changes']}")

    def generate_report(self):
        BannerDisplay.show_info("Report generation feature - Coming soon")

    def export_data(self):
        BannerDisplay.show_info("Data export feature - Coming soon")

    def view_logs(self):
        BannerDisplay.show_info(f"Log file: {self.osint.log_file}")

    def show_bot_info(self):
        result = self.osint.api_call('getMe')
        if result['success']:
            bot = result['data']
            print(f"\n{Colors.INFO}Bot Name:{Colors.RESET} {bot.get('first_name')}")
            print(f"{Colors.INFO}Username:{Colors.RESET} @{bot.get('username')}")
            print(f"{Colors.INFO}Bot ID:{Colors.RESET} {bot.get('id')}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def setup_token(config_manager: ConfigManager) -> str:
    """Interactive token setup"""
    BannerDisplay.show_section_header("Bot Token Configuration")

    if config_manager.token_exists():
        print(f"{Colors.INFO}Existing token found.{Colors.RESET}")
        use_existing = input(f"{Colors.CYAN2}Use existing token? (y/n): {Colors.RESET}").strip().lower()

        if use_existing == 'y':
            return config_manager.load_token()

    print(f"\n{Colors.WARNING}To get a bot token:{Colors.RESET}")
    print(f"  1. Open Telegram and search for @BotFather")
    print(f"  2. Send /newbot and follow instructions")
    print(f"  3. Copy the token provided\n")

    token = input(f"{Colors.CYAN2}[?] Enter your bot token: {Colors.RESET}").strip()

    save = input(f"{Colors.CYAN2}Save token for future use? (y/n): {Colors.RESET}").strip().lower()
    if save == 'y':
        config_manager.save_token(token)

    return token

def main():
    # Clear screen
    os.system('clear' if os.name != 'nt' else 'cls')

    # Show banner
    BannerDisplay.show_main_banner()

    # Initialize folder structure
    folders = FolderStructure()
    BannerDisplay.show_loading("Initializing folder structure")
    folders.initialize()
    BannerDisplay.show_success("Folder structure ready")

    # Setup configuration
    config_manager = ConfigManager(folders.get_path('config'))

    # Get token
    token = setup_token(config_manager)

    if not token:
        BannerDisplay.show_error("No token provided")
        sys.exit(1)

    # Initialize OSINT engine
    BannerDisplay.show_loading("Initializing OSINT engine")
    osint = UserTegOSINT(token, folders)

    # Validate token
    if not osint.validate_token():
        BannerDisplay.show_error("Invalid bot token")
        sys.exit(1)

    BannerDisplay.show_success("Bot connected successfully")

    # Show bot info
    result = osint.api_call('getMe')
    if result['success']:
        bot = result['data']
        print(f"\n{Colors.SUCCESS}Connected as:{Colors.RESET} {bot.get('first_name')} (@{bot.get('username')})")

    # Main menu loop
    menu = MenuSystem(osint)

    while True:
        try:
            menu.show_menu()
            choice = input(f"\n{Colors.CYAN2}{Colors.BOLD}[?] Select option: {Colors.RESET}").strip()

            if not choice.isdigit():
                BannerDisplay.show_error("Invalid input")
                continue

            if not menu.handle_choice(int(choice)):
                break

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] Operation cancelled{Colors.RESET}")
            break
        except Exception as e:
            BannerDisplay.show_error(f"Error: {e}")

    print(f"\n{Colors.CYAN2}{Colors.BOLD}{'═' * 70}")
    print(f"  Thank you for using USERTEG")
    print(f"  Intelligence data saved to: {folders.base_dir}")
    print(f"{'═' * 70}{Colors.RESET}\n")

if __name__ == '__main__':
    main()
