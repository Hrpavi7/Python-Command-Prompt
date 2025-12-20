import os
import subprocess
import platform


class TaskManager:
    @staticmethod
    def list_processes():
        try:
            if platform.system().lower() == "windows":
                cmd = "tasklist"
            else:
                cmd = "ps -A"

            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return result.stdout
        except Exception as e:
            return f"Failed to list processes: {e}"

    @staticmethod
    def kill_process(pid_or_name):
        try:
            if platform.system().lower() == "windows":
                cmd = (
                    f"taskkill /f /im {pid_or_name}"
                    if not pid_or_name.isdigit()
                    else f"taskkill /f /pid {pid_or_name}"
                )
            else:
                cmd = f"kill -9 {pid_or_name}"

            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"Error killing process: {e}"
