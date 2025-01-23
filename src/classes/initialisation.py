import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import time
from network_utils.network_utils import enable_network_discovery, create_shared_folder, get_wlan_ip, start_http_server
from network_utils.network_utils import start_http_server, stop_http_server,get_wlan_ip

from classes.p2pfilesharing import P2PFileSharing

class InitializationWorker(QThread):
    update_status = pyqtSignal(str)
    initialization_complete = pyqtSignal(dict)
    
    def run(self):
        try:
            # Network Discovery
            self.update_status.emit("Starting network discovery...")
            enable_network_discovery()
            time.sleep(2)
            
            # Create Shared Folder
            self.update_status.emit("Creating shared folder...")
            shared_folder = create_shared_folder()
            time.sleep(2)
            
            # Get WLAN IP
            self.update_status.emit("Getting Ip-Address...")
            wlan_ip = get_wlan_ip()
            time.sleep(2)
            
            # Start HTTP Server
            self.update_status.emit("Starting HTTP server...")
            http_server = start_http_server(shared_folder, wlan_ip)
            time.sleep(2)

            
            # Prepare result data
            init_data = {
                "shared_folder": shared_folder,
                "wlan_ip": wlan_ip,
                "http_server": http_server
            }
            print(init_data)
            self.update_status.emit("Initialization Complete!")
            self.initialization_complete.emit(init_data)
            
        except Exception as e:
            self.update_status.emit(f"Error: {str(e)}")


class InitializationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Initialize worker thread
        self.worker = InitializationWorker()
        self.worker.update_status.connect(self.update_status_label)
        self.worker.initialization_complete.connect(self.on_initialization_complete)
        
        # Start initialization after a short delay
        QTimer.singleShot(1000, self.worker.start)
    
    def init_ui(self):
        self.setWindowTitle("Initializing...")
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Center the window
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Create layout with status label
        self.status_label = QLabel("Preparing to initialize...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { font-size: 14px; }")
        
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def update_status_label(self, message):
        self.status_label.setText(message)
    
    def on_initialization_complete(self, init_data):
        # Close initialization window and show home page
        self.close()
        self.home_page = P2PFileSharing(init_data)
        self.home_page.setFixedSize(1000, 910)  # Width: 1066, Height: 768
        # Disable window maximization
        self.home_page.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.home_page.show()
