```markdown
# 🫆 USERTEG - Telegram OSINT Command Center



**Professional Intelligence Gathering System for Telegram**

## 🚀 Features

- **Real-time Message Monitoring** - Log all messages from groups
- **Username History Tracking** - Track username changes over time  
- **Advanced User Intelligence** - Comprehensive user profiling
- **Chat Analytics** - Member statistics and admin analysis
- **Public Channel Search** - Find and analyze public entities
- **SQLite Database** - Persistent data storage and analysis
🛠️ Installation

Prerequisites

· Python 3.7+
· Telegram Bot Token from @BotFather

Quick Start

```bash
# Clone or download the project
git clone <repository-url>
cd usertag

# Run the application
python3 userteg.py
```

First Run Setup

1. The application will create the folder structure automatically
2. Enter your Telegram Bot Token when prompted
3. Choose to save the token securely for future use
4. Add your bot to target groups with appropriate permissions

🎯 Usage

Main Menu Options

🔍 Intelligence Gathering

1. View User Intelligence & History - Complete user profile with username history
2. Search Username - Search current, historical, and public usernames
3. View User's Message History - See all messages from specific users
4. Search Messages by Keyword - Find messages containing specific terms

📊 Real-time Monitoring

1. START Message Monitoring - 24/7 message logging from all groups
2. View Live Database Statistics - Current data metrics and counts

📈 Analysis & Reports

1. Analyze Chat/Channel - Get member counts, admin lists, and chat info
2. Export Data to JSON - Export intelligence reports

⚙️ System Tools

1. View Session Logs - Review operation history
2. Bot Information - Display connected bot details
3. Exit USERTEG - Clean shutdown

🔧 API Methods

Method Purpose Requires
getMe Bot information Token
getChat Chat details Bot in chat
getChatMember User status in chat Bot in chat
getChatAdministrators Admin list Bot in chat
getUpdates Message monitoring Token
getUserProfilePhotos Profile pictures User interaction

🗃️ Database Schema

Users Table

· user_id (Primary Key)
· first_name, last_name
· current_username
· is_bot, language_code
· first_seen, last_seen

Username History

· id (Auto-increment)
· user_id (Foreign Key)
· username
· changed_at (Timestamp)

Messages

· message_id, chat_id (Composite Primary Key)
· user_id, username, first_name
· message_text, message_date
· media_type, forwarded_from

⚠️ Legal & Ethical Usage

✅ Permitted

· Monitoring public groups where bot is a member
· Security research and analysis
· Personal intelligence gathering
· Educational purposes

❌ Prohibited

· Harassment or stalking
· Commercial data selling
· Unauthorized surveillance
· Violating Telegram Terms of Service

🔒 Security

· Bot tokens stored with file permissions 600
· All data stored locally in SQLite
· No external data transmission
· Regular backup recommendations

🐛 Troubleshooting

Common Issues

Token Invalid

```bash
Error: Invalid bot token
Solution: Get new token from @BotFather
```

No Messages Logged

```bash
Issue: Database remains empty
Solution: Ensure bot is added to groups with read permissions
```

Permission Errors

```bash
Issue: Cannot create folders or save files
Solution: Check directory write permissions
```
📞 Support

For issues and questions:

1. Check logs in userteg_data/logs/
2. Verify bot token validity
3. Ensure proper group permissions
4. Review Telegram API documentation
