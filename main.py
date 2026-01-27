import os
import sys
import shutil
import platform
import socket
import subprocess
import json
import configparser
import re
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
cfg_dir = os.path.join(parent_dir, "cfg")
tools_dir = os.path.join(parent_dir, "tools")

# for debugging, you can delete this
# print(f"DEBUG: Script directory: {script_dir}")
# print(f"DEBUG: Parent directory: {parent_dir}")
# print(f"DEBUG: Tools directory: {tools_dir}")
# print(f"DEBUG: Tools folder exists? {os.path.exists(tools_dir)}")
# if os.path.exists(tools_dir):
#    print(f"DEBUG: Files in tools folder: {os.listdir(tools_dir)}")
#
# if os.path.exists(cfg_dir) and cfg_dir not in sys.path:
#    sys.path.insert(0, cfg_dir)
#    print(f"DEBUG: Added cfg_dir to sys.path")
# if os.path.exists(tools_dir) and tools_dir not in sys.path:
#   sys.path.insert(0, tools_dir)
#   print(f"DEBUG: Added tools_dir to sys.path")
#
# print(f"DEBUG: sys.path = {sys.path[:3]}")

try:
    from config_loader import ConfigLoader
except ImportError as e:
    print(f"Warning: Could not import ConfigLoader: {e}")

    class ConfigLoader:
        def __init__(self):
            self.base_dir = "cfg"
            self.config_path = os.path.join(self.base_dir, "config.json")
            self.settings_path = os.path.join(self.base_dir, "settings.ini")
            self.theme_path = os.path.join(self.base_dir, "theme.css")

        def load_json_config(self):
            if not os.path.exists(self.config_path):
                return {
                    "startup_commands": ["echo Config folder/file not found.", "ver"]
                }
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading JSON config: {e}")
                return {"startup_commands": []}

        def load_ini_settings(self):
            config = configparser.ConfigParser()
            if os.path.exists(self.settings_path):
                try:
                    config.read(self.settings_path)
                except Exception as e:
                    print(f"Error loading INI settings: {e}")
            return config

        def load_css_theme(self):
            theme_colors = {
                "background": "black",
                "text": "#e0e0e0",
                "prompt": "#00ff00",
                "error": "#ff0000",
                "caret": "#FFFFFF",
            }
            if not os.path.exists(self.theme_path):
                return theme_colors
            try:
                with open(self.theme_path, "r") as f:
                    content = f.read()
                bg = re.search(r"background-color:\s*(#?[a-zA-Z0-9]+)", content)
                if bg:
                    theme_colors["background"] = bg.group(1)
                txt = re.search(
                    r"\.terminal-text\s*{[^}]*color:\s*(#?[a-zA-Z0-9]+)", content
                )
                if txt:
                    theme_colors["text"] = txt.group(1)
                pr = re.search(
                    r"\.prompt-symbol\s*{[^}]*color:\s*(#?[a-zA-Z0-9]+)", content
                )
                if pr:
                    theme_colors["prompt"] = pr.group(1)
                err = re.search(r"\.error\s*{[^}]*color:\s*(#?[a-zA-Z0-9]+)", content)
                if err:
                    theme_colors["error"] = err.group(1)
            except Exception as e:
                print(f"Error loading CSS theme: {e}")
            return theme_colors


try:
    from network import NetworkTools
except ImportError as e:
    print(f"Warning: Could not import NetworkTools: {e}")
    NetworkTools = None

try:
    from task_manager import TaskManager
except ImportError as e:
    print(f"Warning: Could not import TaskManager: {e}")
    TaskManager = None

try:
    from file_explorer import FileExplorerPopup
except ImportError as e:
    print(f"Warning: Could not import FileExplorerPopup: {e}")
    FileExplorerPopup = None

try:
    from command_logger import CommandLogger
except ImportError as e:
    print(f"Warning: Could not import CommandLogger: {e}")
    CommandLogger = None

if os.name == "nt":
    os.system("color")

colors = {
    "1": "white",
    "2": "green2",
    "3": "yellow",
    "4": "dodgerblue",
    "5": "purple1",
    "6": "cyan",
    "7": "white",
    "reset": "white",
    "red": "red",
    "green": "green2",
    "yellow": "yellow",
    "blue": "dodgerblue",
    "purple": "purple1",
    "cyan": "cyan",
    "white": "white",
    "gray": "gray60",
}


class TkinterCLI:
    def __init__(self, root):
        self.root = root
        self.current_color = colors["1"]
      
        self.logger = (
            CommandLogger(log_dir=os.path.join(parent_dir, "logs"))
            if CommandLogger
            else None
        )
        if self.logger:
            self.logger.log_session_start()

        self.loader = ConfigLoader()
        self.json_config = self.loader.load_json_config()
        self.ini_settings = self.loader.load_ini_settings()
        self.theme = self.loader.load_css_theme()

        width = self.ini_settings.get("WindowSettings", "width", fallback="850")
        height = self.ini_settings.get("WindowSettings", "height", fallback="550")
        title = self.ini_settings.get(
            "WindowSettings", "title", fallback="Python Command Prompt"
        )

        self.root.title(title)
        self.root.geometry(f"{width}x{height}")

        bg_color = self.theme["background"]
        text_color = self.theme["text"]
        caret_color = self.theme["caret"]

        self.root.configure(bg=bg_color)

        self.command_history = []

        self.output = scrolledtext.ScrolledText(
            root,
            bg=bg_color,
            fg=text_color,
            insertbackground=caret_color,
            font=("Consolas", 11),
        )
        self.output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output.config(state=tk.DISABLED)

        self.input_frame = tk.Frame(root, bg=bg_color)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.prompt_label = tk.Label(
            self.input_frame,
            text=">",
            bg=bg_color,
            fg=self.theme["prompt"],
            font=("Consolas", 12, "bold"),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            self.input_frame,
            bg=bg_color,
            fg=text_color,
            insertbackground=caret_color,
            font=("Consolas", 12),
            borderwidth=0,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.process_command)
        self.entry.focus_set()

        startup_cmds = self.json_config.get("startup_commands", [])
        if startup_cmds:
            for cmd in startup_cmds:
                self.run_silent_command(cmd)
        else:
            self.write_to_screen(f"Microsoft Windows [Version {platform.version()}]")
            self.write_to_screen("(c) Microsoft Corporation. All rights reserved.\n")

    def write_to_screen(self, text, color=None):
        if color is None:
            color = self.current_color

        if color == "red":
            color = self.theme["error"]
        elif color == "gray":
            color = "gray60"

        self.output.config(state=tk.NORMAL)

        tag_name = f"color_{color}".replace("#", "hex")
        self.output.tag_config(tag_name, foreground=color)
        self.output.insert(tk.END, text + "\n", tag_name)

        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def run_silent_command(self, full_command):
        parts = full_command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        self.execute_logic(cmd, args, silent=True)

    def process_command(self, event):
        user_input = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not user_input:
            return

        self.command_history.append(user_input)

        if self.logger:
            try:
                username = os.getlogin()
            except:
                username = "unknown"
            self.logger.log_command(user_input, username=username)

        self.write_to_screen(f"{os.getcwd()}> {user_input}", color=self.theme["prompt"])

        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        self.execute_logic(cmd, args, silent=False)

    def execute_logic(self, cmd, args, silent=False):
        commands = {
            "quit": self.root.quit,
            "q": self.root.quit,
            "exit": self.root.quit,
            "help": self.show_help,
            "h": self.show_help,
            "clear": self.clear_screen,
            "cls": self.clear_screen,
            "date": self.show_date,
            "time": self.show_time,
            "ls": self.list_files,
            "dir": self.list_files,
            "pwd": self.show_pwd,
            "echo": lambda: self.write_to_screen(args),
            "cd": lambda: self.change_directory(args),
            "mkdir": lambda: self.make_directory(args),
            "rm": lambda: self.remove_item(args),
            "del": lambda: self.remove_item(args),
            "touch": lambda: self.touch_file(args),
            "color": lambda: self.change_color(args),
            "colors": self.show_colors,
            "ver": self.show_ver,
            "whoami": self.show_whoami,
            "hostname": self.show_hostname,
            "type": lambda: self.cat_file(args),
            "tree": self.show_tree,
            "systeminfo": self.show_system_info,
            "calc": lambda: self.run_calc(args),
            "start": lambda: self.start_file(args),
            "history": self.show_history,
            "logs": self.show_logs,
            "easteregg": lambda: self.write_to_screen("🥚 67 67 67..."),
        }

        if cmd in commands:
            try:
                if callable(commands[cmd]):
                    commands[cmd]()
            except Exception as e:
                self.write_to_screen(f"Execution Error: {e}", "red")

        elif cmd == "ping" and NetworkTools:
            self.write_to_screen(f"Pinging {args}...")
            result = NetworkTools.ping(args)
            self.write_to_screen(result)

        elif cmd == "ipconfig" and NetworkTools:
            ip = NetworkTools.get_ip()
            self.write_to_screen(f"Local IP: {ip}")

        elif cmd == "tasklist" and TaskManager:
            self.write_to_screen("Fetching process list...")
            processes = TaskManager.list_processes()
            self.write_to_screen(processes)

        elif cmd == "taskkill" and TaskManager:
            if not args:
                self.write_to_screen("Usage: taskkill <name or pid>", "red")
            else:
                result = TaskManager.kill_process(args)
                self.write_to_screen(result)

        elif cmd == "explorer" and FileExplorerPopup:
            FileExplorerPopup(self.root)
            self.write_to_screen("Opening File Explorer window...")

        else:
            if not silent:
                self.write_to_screen(f"'{cmd}' is not recognized as a command.", "red")

    def clear_screen(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def show_help(self):
        help_text = """Available Commands:
    help, h      - Show this help message
    clear, cls   - Clear the screen
    dir, ls      - List files in directory
    cd <path>    - Change directory
    pwd          - Show current path
    date, time   - Show current date/time
    mkdir <name> - Create directory
    rm, del      - Remove file or directory
    touch <file> - Create empty file
    type <file>  - Display file contents
    start <file> - Open file in default app
    tree         - Show folder structure
    ver          - Show OS version
    whoami       - Show current user
    hostname     - Show computer name
    systeminfo   - Show system specs
    calc <expr>  - Calculate math (e.g. calc 5*5)
    color <name> - Change text color
    colors       - List available colors
    history      - Show command history
    explorer     - Opens file explorer (if available)
    ping <host>  - Ping a host (if network tools available)
    ipconfig     - Show local IP (if network tools available)
    tasklist     - Show running processes (if task manager available)
    taskkill     - Kill a process (if task manager available)
    exit, quit   - Close terminal
        """
        self.write_to_screen(help_text, "gray")

    def show_colors(self):
        self.write_to_screen("Available colors: " + ", ".join(colors.keys()))

    def change_color(self, choice):
        choice = choice.lower().strip()
        if choice in colors:
            self.current_color = colors[choice]
            self.write_to_screen(f"Color changed to {choice}", self.current_color)
        else:
            self.write_to_screen(
                "Color not found. Use 'colors' to see available colors.", "red"
            )

    def list_files(self):
        try:
            items = os.listdir(".")
            dirs = sorted([d for d in items if os.path.isdir(d)])
            files = sorted([f for f in items if os.path.isfile(f)])

            if not dirs and not files:
                self.write_to_screen("Directory is empty.")
                return

            for d in dirs:
                self.write_to_screen(f"<DIR> {d}")
            for f in files:
                size = os.path.getsize(f)
                self.write_to_screen(f"      {f} ({size} bytes)")
        except PermissionError:
            self.write_to_screen("Error: Permission denied.", "red")
        except Exception as e:
            self.write_to_screen(f"Error: {e}", "red")

    def show_tree(self):
        self.write_to_screen(f"Folder PATH listing for volume {os.getcwd()}")
        try:
            for root_dir, dirs, files in os.walk(".", topdown=True):
                level = root_dir.replace(".", "", 1).count(os.sep)
                indent = "|   " * level
                dirname = os.path.basename(root_dir) or "."
                self.write_to_screen(f"{indent}|-- {dirname}/")
                subindent = "|   " * (level + 1)
                for f in files:
                    if level < 2:
                        self.write_to_screen(f"{subindent}|-- {f}")
        except Exception as e:
            self.write_to_screen(f"Error: {e}", "red")

    def cat_file(self, filename):
        if not filename:
            self.write_to_screen("Error: Specify a file name.", "red")
            return
        try:
            if not os.path.exists(filename):
                self.write_to_screen(f"Error: File '{filename}' not found.", "red")
                return
            if not os.path.isfile(filename):
                self.write_to_screen(f"Error: '{filename}' is not a file.", "red")
                return
            with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if content:
                    self.write_to_screen(content)
                else:
                    self.write_to_screen("(File is empty)")
        except Exception as e:
            self.write_to_screen(f"Error reading file: {e}", "red")

    def start_file(self, filename):
        if not filename:
            self.write_to_screen("Error: Specify a file to open.", "red")
            return
        try:
            if not os.path.exists(filename):
                self.write_to_screen(f"Error: '{filename}' not found.", "red")
                return
            if os.name == "nt":
                os.startfile(filename)
            elif sys.platform == "darwin":
                subprocess.call(["open", filename])
            else:
                subprocess.call(["xdg-open", filename])
            self.write_to_screen(f"Opening {filename}...")
        except Exception as e:
            self.write_to_screen(f"Error starting file: {e}", "red")

    def change_directory(self, path):
        try:
            target = path if path else os.path.expanduser("~")
            if not os.path.exists(target):
                self.write_to_screen(
                    "The system cannot find the path specified.", "red"
                )
                return
            os.chdir(target)
            self.write_to_screen(f"Changed directory to: {os.getcwd()}")
        except PermissionError:
            self.write_to_screen("Error: Permission denied.", "red")
        except Exception as e:
            self.write_to_screen(f"Error: {e}", "red")

    def make_directory(self, names):
        if not names:
            self.write_to_screen("Error: Specify a directory name.", "red")
            return
        for folder in names.split():
            try:
                os.mkdir(folder)
                self.write_to_screen(f"Created directory: {folder}")
            except FileExistsError:
                self.write_to_screen(
                    f"Error: Directory '{folder}' already exists.", "red"
                )
            except Exception as e:
                self.write_to_screen(f"Error: {e}", "red")

    def remove_item(self, path):
        if not path:
            self.write_to_screen("Error: Specify a file or directory to remove.", "red")
            return
        try:
            if not os.path.exists(path):
                self.write_to_screen(f"Could not find {path}", "red")
                return
            if os.path.isdir(path):
                os.rmdir(path)
                self.write_to_screen(f"Deleted directory: {path}")
            elif os.path.isfile(path):
                os.remove(path)
                self.write_to_screen(f"Deleted file: {path}")
        except OSError as e:
            if "not empty" in str(e).lower():
                self.write_to_screen(
                    f"Error: Directory not empty. Use rmdir or delete files first.",
                    "red",
                )
            else:
                self.write_to_screen(f"Error: {e}", "red")
        except Exception as e:
            self.write_to_screen(f"Error: {e}", "red")

    def touch_file(self, names):
        if not names:
            self.write_to_screen("Error: Specify a file name.", "red")
            return
        for filename in names.split():
            try:
                with open(filename, "a"):
                    pass
                self.write_to_screen(f"Created/touched: {filename}")
            except Exception as e:
                self.write_to_screen(f"Error: {e}", "red")

    def run_calc(self, expression):
        if not expression:
            self.write_to_screen("Error: Provide a math expression.", "red")
            return
        try:
            allowed_chars = "0123456789+-*/(). "
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                self.write_to_screen(f"= {result}")
            else:
                self.write_to_screen(
                    "Error: Invalid characters in math expression.", "red"
                )
        except ZeroDivisionError:
            self.write_to_screen("Math Error: Division by zero.", "red")
        except Exception as e:
            self.write_to_screen(f"Math Error: {e}", "red")

    def show_ver(self):
        self.write_to_screen(f"Microsoft Windows [Version {platform.version()}]")

    def show_whoami(self):
        try:
            username = os.getlogin()
            hostname = platform.node()
            self.write_to_screen(f"{hostname}\\{username}")
        except Exception:
            self.write_to_screen(f"{platform.node()}\\unknown")

    def show_hostname(self):
        self.write_to_screen(socket.gethostname())

    def show_system_info(self):
        self.write_to_screen(f"Host Name:             {socket.gethostname()}")
        self.write_to_screen(f"OS Name:               {platform.system()}")
        self.write_to_screen(f"OS Version:            {platform.version()}")
        self.write_to_screen(f"System Type:           {platform.machine()}")
        self.write_to_screen(
            f"Processor:             {platform.processor() or 'Unknown'}"
        )

    def show_date(self):
        self.write_to_screen(
            f"The current date is: {datetime.now().strftime('%A %m/%d/%Y')}"
        )

    def show_time(self):
        self.write_to_screen(
            f"The current time is: {datetime.now().strftime('%H:%M:%S.%f')[:-4]}"
        )

    def show_pwd(self):
        self.write_to_screen(os.getcwd())

    def show_history(self):
        if not self.command_history:
            self.write_to_screen("No command history.")
            return
        for idx, cmd in enumerate(self.command_history, 1):
            self.write_to_screen(f"{idx}: {cmd}")

    def show_logs(self):
        if not self.logger:
            self.write_to_screen("Logging is not available.", "red")
            return

        logs = self.logger.get_today_logs()
        self.write_to_screen("--- Today's Command Logs ---")
        self.write_to_screen(logs)


if __name__ == "__main__":
    root = tk.Tk()
    app = TkinterCLI(root)

    def on_closing():
        if app.logger:
            app.logger.log_session_end()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
