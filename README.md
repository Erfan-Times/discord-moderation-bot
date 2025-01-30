# Discord Moderation Bot

A feature-rich Discord moderation bot with comprehensive logging capabilities.

## Features

### Moderation Commands
- `/kick` - Kick members with confirmation prompts
- `/ban` - Ban members with message deletion options
- `/timeout` - Temporarily mute members
- `/purge` - Delete multiple messages with filters
- `/warn` - Issue warnings to users
- `/warnings` - View user warning history

### Role Management
- `/addrole` - Assign roles to members
- `/removerole` - Remove roles from members
- `/createrole` - Create new server roles
- `/deleterole` - Delete existing roles
- `/roleinfo` - View detailed role information

### Information Commands
- `/userinfo` - Display detailed user information
- `/serverinfo` - Show server statistics and details
- `/help` - List all available commands

### Advanced Features
- Message content filtering
- Anti-spam protection
- Confirmation prompts for destructive actions
- Comprehensive audit logging
- Detailed error handling

### Enhanced Logging System
- Color-coded console output
- Timezone-aware timestamps
- Structured log format
- Four log categories:
  - Command execution logs
  - Event tracking
  - System operations
  - Moderation audit logs

## Setup

1. Clone the repository:
```bash
git clone https://github.com/kozydot/discord-moderation-bot.git
cd discord-moderation-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_bot_token_here
LOG_CHANNEL_ID=your_log_channel_id_here
```

4. Run the bot:
```bash
python main.py
```

## Required Permissions

The bot requires the following permissions:
- Manage Roles
- Kick Members
- Ban Members
- Manage Messages
- View Channels
- Send Messages
- Read Message History
- Add Reactions
- Moderate Members

## Configuration

### Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable required Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
   - Presence Intent

### Log Channel
1. Create a private channel for logs in your Discord server
2. Right-click the channel and copy the ID
3. Add the channel ID to your `.env` file

## Log Examples

### Command Execution
```
[03:57 PM] INFO     [COMMAND] Command 'kick' completed
  Command: kick
  User: Moderator#1234
  Server: My Discord Server
  Channel: #general
  Status: completed
```

### Moderation Action
```
[03:57 PM] INFO     [AUDIT] Audit: kick performed by Moderator#1234 on User#5678
  Action: kick
  Moderator: Moderator#1234
  Target: User#5678
  Reason: Violation of rules
```

### System Operations
```
[03:57 PM] INFO     [SYSTEM] Bot is starting up
  Operation: startup
  System: Windows
  Python: 3.12.0
```

## Project Structure
```
discord-moderation-bot/
├── main.py              # Bot initialization and core setup
├── requirements.txt     # Project dependencies
├── .env                 # Configuration file
├── cogs/               # Command modules
│   ├── moderation.py   # Kick, ban, timeout commands
│   ├── message_mod.py  # Message management, filtering
│   ├── info.py         # User/server information
│   ├── roles.py        # Role management
│   └── help.py         # Help command system
└── utils/              # Utility modules
    └── logger.py       # Enhanced logging system
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
