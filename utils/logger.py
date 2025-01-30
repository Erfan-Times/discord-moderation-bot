import logging
import sys
from datetime import datetime
import pytz
from typing import Optional, Any, Dict
import json
import traceback
from pathlib import Path
from colorama import Fore, Style, init
import platform

# Initialize colorama for Windows support
init()

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and structured, readable output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    METADATA_COLORS = {
        'COMMAND': Fore.BLUE,
        'EVENT': Fore.MAGENTA,
        'SYSTEM': Fore.CYAN,
        'AUDIT': Fore.YELLOW
    }

    def __init__(self, timezone: pytz.timezone):
        super().__init__()
        self.timezone = timezone

    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context data in a clean, readable format."""
        if not context:
            return ""

        lines = []
        
        # Command-specific formatting
        if 'command' in context:
            cmd_info = [
                f"{Fore.WHITE}Command:{Style.RESET_ALL} {context.get('command')}",
                f"{Fore.WHITE}User:{Style.RESET_ALL} {context.get('user')}",
                f"{Fore.WHITE}Server:{Style.RESET_ALL} {context.get('guild')}"
            ]
            
            if 'channel' in context:
                cmd_info.append(f"{Fore.WHITE}Channel:{Style.RESET_ALL} #{context.get('channel')}")
                
            if 'status' in context:
                status_color = Fore.GREEN if context['status'] == 'completed' else (
                    Fore.RED if context['status'] in ['failed', 'error'] else Fore.YELLOW
                )
                cmd_info.append(f"{Fore.WHITE}Status:{Style.RESET_ALL} {status_color}{context.get('status')}{Style.RESET_ALL}")

            lines.extend(cmd_info)

        # Event-specific formatting
        elif 'event' in context:
            event_info = [f"{Fore.WHITE}Event:{Style.RESET_ALL} {context.get('event')}"]
            if 'details' in context and context['details']:
                for key, value in context['details'].items():
                    event_info.append(f"{Fore.WHITE}{key}:{Style.RESET_ALL} {value}")
            lines.extend(event_info)

        # Audit-specific formatting
        elif 'action' in context:
            audit_info = [
                f"{Fore.WHITE}Action:{Style.RESET_ALL} {context.get('action')}",
                f"{Fore.WHITE}Moderator:{Style.RESET_ALL} {context.get('user')}",
                f"{Fore.WHITE}Target:{Style.RESET_ALL} {context.get('target')}"
            ]
            if 'details' in context and context['details']:
                for key, value in context['details'].items():
                    audit_info.append(f"{Fore.WHITE}{key}:{Style.RESET_ALL} {value}")
            lines.extend(audit_info)

        # System-specific formatting
        elif 'operation' in context:
            system_info = [f"{Fore.WHITE}Operation:{Style.RESET_ALL} {context.get('operation')}"]
            if 'system' in context:
                system_info.append(f"{Fore.WHITE}System:{Style.RESET_ALL} {context.get('system')}")
            if 'python_version' in context:
                system_info.append(f"{Fore.WHITE}Python:{Style.RESET_ALL} {context.get('python_version')}")
            lines.extend(system_info)

        return "\n  " + "\n  ".join(lines) if lines else ""

    def format(self, record: logging.LogRecord) -> str:
        # Add timezone info to the timestamp
        created = datetime.fromtimestamp(record.created)
        created = pytz.utc.localize(created).astimezone(self.timezone)
        
        # Format timestamp in 12-hour format
        record.timestamp = created.strftime("%I:%M:%S %p")
        
        # Add color to the level name
        level_color = self.COLORS.get(record.levelname, '')
        colored_levelname = f"{level_color}{record.levelname:<8}{Style.RESET_ALL}"

        # Format the message
        message_lines = []

        # Add metadata color if available
        metadata_str = ""
        if hasattr(record, 'metadata'):
            metadata_color = self.METADATA_COLORS.get(record.metadata, Fore.WHITE)
            metadata_str = f"{metadata_color}[{record.metadata}]{Style.RESET_ALL} "

        # Build the base log line
        base_line = f"{Fore.WHITE}[{record.timestamp}]{Style.RESET_ALL} {colored_levelname} {metadata_str}{str(record.msg)}"
        message_lines.append(base_line)

        # Add formatted context if available
        if hasattr(record, 'context') and record.context:
            context_str = self.format_context(record.context)
            if context_str:
                message_lines.append(context_str)

        # Add error information if available
        if record.exc_info:
            error_lines = traceback.format_exception(*record.exc_info)
            message_lines.append(f"{Fore.RED}Error Details:{Style.RESET_ALL}")
            message_lines.extend(f"  {line.rstrip()}" for line in error_lines)

        return "\n".join(message_lines)

class DiscordLogger:
    """Enhanced logger for Discord bot with rich formatting and metadata."""

    def __init__(self, bot_name: str, timezone_str: str = "UTC"):
        self.bot_name = bot_name
        try:
            self.timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            print(f"Warning: Unknown timezone {timezone_str}, falling back to UTC")
            self.timezone = pytz.UTC
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create the logger
        self.logger = logging.getLogger(self.bot_name)
        self.logger.setLevel(logging.DEBUG)

        # Create console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(self.timezone))
        console_handler.setLevel(logging.INFO)
        
        # Create file handler for all logs
        current_time = datetime.now(self.timezone).strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            f"logs/{self.bot_name}_{current_time}.log",
            encoding='utf-8'
        )
        # Use more detailed format for file logs
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s\n%(context)s\n',
            datefmt='%Y-%m-%d %I:%M:%S %p %Z'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def _log(self, 
             level: int, 
             message: str, 
             metadata: Optional[str] = None, 
             context: Optional[Dict[str, Any]] = None,
             exc_info: Optional[tuple] = None):
        """Internal method to handle logging with metadata and context."""
        if context is None:
            context = {}
        context['timestamp'] = datetime.now(self.timezone).isoformat()
        extra = {'metadata': metadata, 'context': context}
        self.logger.log(level, message, exc_info=exc_info, extra=extra)

    def command(self, 
                command_name: str, 
                user: str, 
                guild: str, 
                status: str = "started", 
                error: Optional[Exception] = None,
                channel: Optional[str] = None,
                **kwargs):
        """Log command execution with rich context."""
        context = {
            'command': command_name,
            'user': user,
            'guild': guild,
            'status': status,
            'channel': channel,
            **kwargs
        }

        if error:
            self._log(
                logging.ERROR,
                f"Command '{command_name}' failed",
                metadata="COMMAND",
                context=context,
                exc_info=(type(error), error, error.__traceback__)
            )
        else:
            level = logging.INFO if status == "completed" else logging.DEBUG
            self._log(
                level,
                f"Command '{command_name}' {status}",
                metadata="COMMAND",
                context=context
            )

    def event(self, 
              event_name: str, 
              details: Optional[Dict[str, Any]] = None,
              error: Optional[Exception] = None):
        """Log Discord events with context."""
        context = {
            'event': event_name,
            'details': details or {}
        }

        if error:
            self._log(
                logging.ERROR,
                f"Event '{event_name}' encountered an error",
                metadata="EVENT",
                context=context,
                exc_info=(type(error), error, error.__traceback__)
            )
        else:
            self._log(
                logging.INFO,
                f"Event '{event_name}' triggered",
                metadata="EVENT",
                context=context
            )

    def system(self, 
               message: str, 
               operation: Optional[str] = None,
               error: Optional[Exception] = None):
        """Log system-level operations."""
        context = {
            'operation': operation,
            'system': platform.system(),
            'python_version': platform.python_version()
        }

        if error:
            self._log(
                logging.ERROR,
                message,
                metadata="SYSTEM",
                context=context,
                exc_info=(type(error), error, error.__traceback__)
            )
        else:
            self._log(
                logging.INFO,
                message,
                metadata="SYSTEM",
                context=context
            )

    def audit(self, 
              action: str, 
              user: str, 
              target: str, 
              details: Optional[Dict[str, Any]] = None):
        """Log moderation actions for audit purposes."""
        context = {
            'action': action,
            'user': user,
            'target': target,
            'details': details or {}
        }

        self._log(
            logging.INFO,
            f"Audit: {action} performed by {user} on {target}",
            metadata="AUDIT",
            context=context
        )

# Export default logger instance
bot_logger = DiscordLogger("ModBot", "Asia/Dubai")
