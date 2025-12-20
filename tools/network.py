import socket
import subprocess
import platform


class NetworkTools:
    @staticmethod
    def get_ip():
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def ping(host):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "4", host]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Ping failed: {e}"

    @staticmethod
    def get_public_ip():
        return "Feature requires 'requests' library."
