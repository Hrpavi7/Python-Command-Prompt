import os
from datetime import datetime

class CommandLogger:
    def __init__(self, log_dir="logs"):
        """Initialize the logger and create logs directory if needed."""
        self.log_dir = log_dir
        self.log_file = None
        self.setup_logging()

    def setup_logging(self):
        """Create logs directory and initialize log file."""

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"Created logs directory: {self.log_dir}")

        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"commands_{today}.log")

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write(f"Command Log - {today}\n")
                f.write("=" * 70 + "\n\n")

    def log_command(self, command, username=None, status="SUCCESS"):
        """
        Log a command with timestamp.

        Args:
            command (str): The command that was executed
            username (str): Optional username
            status (str): Command status (SUCCESS, ERROR, etc.)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_entry = f"[{timestamp}]"

            if username:
                log_entry += f" [{username}]"

            log_entry += f" [{status}] {command}\n"

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            print(f"Logging error: {e}")

    def log_error(self, command, error_message):
        """Log a command that resulted in an error."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [ERROR] {command}\n"
            log_entry += f"    └─> Error: {error_message}\n"

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            print(f"Logging error: {e}")

    def log_session_start(self):
        """Log the start of a new session."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- Session Started: {timestamp} ---\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def log_session_end(self):
        """Log the end of a session."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"--- Session Ended: {timestamp} ---\n\n")
        except Exception as e:
            print(f"Logging error: {e}")

    def get_today_logs(self):
        """Read and return today's log contents."""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return "No logs for today."
        except Exception as e:
            return f"Error reading logs: {e}"

    def list_all_logs(self):
        """List all log files in the logs directory."""
        try:
            if not os.path.exists(self.log_dir):
                return []

            log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".log")]
            return sorted(log_files, reverse=True)  # Most recent first
        except Exception as e:
            print(f"Error listing logs: {e}")
            return []

    def clear_old_logs(self, days_to_keep=30):
        """Delete log files older than specified days."""
        try:
            if not os.path.exists(self.log_dir):
                return 0

            deleted_count = 0
            current_time = datetime.now()

            for filename in os.listdir(self.log_dir):
                if filename.endswith(".log"):
                    filepath = os.path.join(self.log_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age_days = (current_time - file_time).days

                    if age_days > days_to_keep:
                        os.remove(filepath)
                        deleted_count += 1
                        print(f"Deleted old log: {filename}")

            return deleted_count
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return 0

if __name__ == "__main__":
    logger = CommandLogger()

    logger.log_session_start()

    logger.log_command("help", username="maria", status="SUCCESS")
    logger.log_command("ls", username="maria", status="SUCCESS")
    logger.log_command("cd /home", username="maria", status="SUCCESS")
    logger.log_error("rm important.txt", "Permission denied")

    logger.log_session_end()

    print("\n--- Today's Logs ---")
    print(logger.get_today_logs())

    print("\n--- All Log Files ---")
    for log_file in logger.list_all_logs():
        print(f"  - {log_file}")
