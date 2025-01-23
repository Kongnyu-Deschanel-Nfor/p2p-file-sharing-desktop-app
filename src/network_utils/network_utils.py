import os
import sys
import os
import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import platform
import subprocess


def start_http_server(shared_folder, wlan_ip, port=64547):
    """Start an HTTP server to serve the shared folder."""
    try:
        # Change working directory to the shared folder
        os.chdir(shared_folder)

        # Define the HTTP server
        httpd = HTTPServer((wlan_ip, port), SimpleHTTPRequestHandler)
        print(f"HTTP server running at http://{wlan_ip}:{port}")

        # Run the server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        return httpd
    except Exception as e:
        print("Error starting HTTP server:", e)
        raise

def stop_http_server(httpd):
    """Stop the HTTP server."""
    try:
        if httpd:
            httpd.shutdown()
            httpd.server_close()
            print("HTTP server stopped successfully.")
        else:
            print("HTTP server instance is None. Cannot stop.")
    except Exception as e:
        print("Error stopping HTTP server:", e)
        raise


def enable_network_discovery():
    """Run the network discovery script based on the platform."""
    try:
        script_dir = os.path.join(os.getcwd(), "scripts")

        if platform.system() == "Windows":
            script_path = os.path.join(script_dir, "turn-discovery.cmd")
            subprocess.run(["cmd", "/c", script_path], check=True, shell=True)
        elif platform.system() == "Linux":
            script_path = os.path.join(script_dir, "turn-discovery.sh")
            subprocess.run(["bash", script_path], check=True, shell=True)
        else:
            raise OSError("Unsupported operating system for network discovery.")

        print("Network discovery script executed successfully.")
    except Exception as e:
        print("Error executing network discovery script:", e)
        raise




def create_shared_folder():
    """Create a shared folder in the Documents directory."""
    try:
        documents_folder = os.path.expanduser("~/Documents")
        shared_folder = os.path.join(documents_folder, "00ap2pSHARESPHERE")

        if not os.path.exists(shared_folder):
            os.makedirs(shared_folder)
            print(f"Shared folder created at: {shared_folder}")
        else:
            print(f"Shared folder already exists at: {shared_folder}")

        return shared_folder
    except Exception as e:
        print("Error creating shared folder:", e)
        raise



def get_wlan_ip():
        try:
            if sys.platform.startswith('win'):
                # Windows: Get Wireless LAN IP for all adapters
                output = subprocess.check_output('ipconfig', text=True, encoding='utf-8')
                adapters = output.split('Wireless LAN adapter')
                for adapter in adapters[1:]:  # Skip the first section, as it is not an adapter
                    if 'Wi-Fi' in adapter:  # Ensure only Wi-Fi section is considered
                        lines = adapter.split('\n')
                        for line in lines:
                            if 'IPv4 Address' in line or 'IPv4-Adresse' in line:  # Covers localized output
                                ip = line.split(':')[1].strip()
                                if ip:
                                    return ip

            else:
                # Unix-based systems: Get IP address
                interfaces = subprocess.check_output("ip -o addr show | grep wlan", shell=True, text=True)
                for line in interfaces.splitlines():
                    if "inet " in line and "wlan" in line:  # Ensure only WLAN interfaces are considered
                        ip = line.split()[3].split('/')[0]
                        return ip

        except Exception as e:
            print(f"Error getting WLAN IP: {e}")
        return None


def toggle_server(self):
        if self.server_running:
            stop_http_server(self.init_data["http_server"])
        else:
            start_http_server(self.init_data["shared_folder"], self.init_data["wlan_ip"])
        self.server_running = not self.server_running
        self.network_stats.setText(
            f"USER STATUS: {'ONLINE' if self.server_running else 'OFFLINE'}\n"
            
        )
        self.server_toggle.setText("Stop Server" if self.server_running else "Start Server")
        self.server_toggle.setStyleSheet("""
            QPushButton {
                background-color: %s;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: %s;
            }
        """ % (("#dc3545", "#c82333") if self.server_running else ("#28a745", "#218838")))
