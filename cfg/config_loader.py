import json
import configparser
import re
import os


class ConfigLoader:
    def __init__(self):
        self.config_path = "config.json"
        self.settings_path = "settings.ini"
        self.theme_path = "theme.css"

    def load_json_config(self):
        default_config = {"startup_commands": [], "application": {}}
        if not os.path.exists(self.config_path):
            return default_config

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return default_config

    def load_ini_settings(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.settings_path):
            config.read(self.settings_path)
        return config

    def load_css_theme(self):
        theme_colors = {
            "background": "black",
            "text": "white",
            "prompt": "green",
            "error": "red",
            "caret": "white",
        }

        if not os.path.exists(self.theme_path):
            return theme_colors

        try:
            with open(self.theme_path, "r") as f:
                css_content = f.read()

            bg_match = re.search(
                r"body\s*{[^}]*background-color:\s*(#[a-fA-F0-9]+)", css_content
            )
            if bg_match:
                theme_colors["background"] = bg_match.group(1)

            text_match = re.search(
                r"\.terminal-text\s*{[^}]*color:\s*(#[a-fA-F0-9]+)", css_content
            )
            if text_match:
                theme_colors["text"] = text_match.group(1)

            prompt_match = re.search(
                r"\.prompt-symbol\s*{[^}]*color:\s*(#[a-fA-F0-9]+)", css_content
            )
            if prompt_match:
                theme_colors["prompt"] = prompt_match.group(1)

            err_match = re.search(
                r"\.error-msg\s*{[^}]*color:\s*(#[a-fA-F0-9]+)", css_content
            )
            if err_match:
                theme_colors["error"] = err_match.group(1)

            input_match = re.search(
                r"\.input-area\s*{[^}]*caret-color:\s*(#[a-fA-F0-9]+)", css_content
            )
            if input_match:
                theme_colors["caret"] = input_match.group(1)

        except Exception as e:
            print(f"Error parsing CSS: {e}")

        return theme_colors
